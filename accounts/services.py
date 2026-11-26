"""Transactional application lifecycle operations."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from matching.advanced import suggest_improvements

from .matching import match_student, requirements_for, skill_levels_for
from .models import Application, Notification, Opportunity, User

MIN_PROFILE_SKILLS = 3


@transaction.atomic
def delete_empty_opportunity(faculty, opportunity_id):
    if faculty.role != faculty.Role.FACULTY or faculty.is_superuser:
        raise PermissionDenied
    opportunity = (
        Opportunity.objects.visible().select_for_update().get(pk=opportunity_id, faculty=faculty)
    )
    if opportunity.applications.exists():
        raise ValidationError(
            "This opportunity has applications. Close it instead to preserve records."
        )
    opportunity.delete()


@transaction.atomic
def set_user_active(actor, user_id, active):
    if not actor.is_superuser:
        raise PermissionDenied
    user = User.objects.select_for_update().get(pk=user_id)
    if user.pk == actor.pk or user.is_superuser or user.is_staff:
        raise PermissionDenied
    user.is_active = active
    user.save(update_fields=["is_active"])
    return user


@transaction.atomic
def set_opportunity_removed(actor, opportunity_id, removed):
    if not actor.is_superuser:
        raise PermissionDenied
    opportunity = Opportunity.objects.select_for_update().get(pk=opportunity_id)
    opportunity.is_removed = removed
    opportunity.removed_at = timezone.now() if removed else None
    opportunity.save(update_fields=["is_removed", "removed_at"])
    return opportunity


def close_expired_opportunities(today=None):
    today = today or timezone.localdate()
    return (
        Opportunity.objects.visible()
        .filter(status=Opportunity.Status.PUBLISHED, deadline__lt=today)
        .update(status=Opportunity.Status.CLOSED)
    )


def profile_completeness(
    branch, academic_year, interests, skills_count, projects_count, certifications_count
):
    checklist = (
        ("Academic details", bool(branch and branch.strip() and academic_year), "profile_edit"),
        ("Interests", bool(interests and interests.strip()), "profile_edit"),
        ("At least three skills", skills_count >= MIN_PROFILE_SKILLS, "skills"),
        ("At least one project", projects_count >= 1, "projects"),
        ("At least one certification", certifications_count >= 1, "certifications"),
    )
    return {"score": 20 * sum(item[1] for item in checklist), "checklist": checklist}


def recommend_opportunities(student, n):
    levels = skill_levels_for(student)
    active = (
        Application.objects.filter(student=student)
        .exclude(status=Application.Status.WITHDRAWN)
        .values("opportunity_id")
    )
    opportunities = (
        Opportunity.objects.is_open()
        .exclude(pk__in=active)
        .select_related("faculty")
        .prefetch_related("requirements__skill")
    )
    results = []
    for item in opportunities:
        item.match_result = match_student(requirements_for(item), student, skill_levels=levels)
        if item.match_result.score is not None and item.match_result.score > 0:
            item.matched_skills = [
                skill.name for skill in item.match_result.skills if skill.status == "matched"
            ]
            results.append(item)
    return sorted(
        results, key=lambda item: (-item.match_result.score, item.deadline, item.title, item.pk)
    )[:n]


def student_improvements(student):
    levels = skill_levels_for(student)
    opportunities = Opportunity.objects.is_open().prefetch_related("requirements__skill")
    items = suggest_improvements(levels, [requirements_for(item) for item in opportunities])
    existing = {item.skill_id: item for item in student.student_skills.all()}
    return [
        {
            "item": item,
            "gain": float(item.gain),
            "average": float(item.gain / item.opportunities_affected),
            "existing": existing.get(item.skill_id),
        }
        for item in items
    ]


@transaction.atomic
def apply_to_opportunity(student, opportunity_id):
    opportunity = Opportunity.objects.visible().select_for_update().get(pk=opportunity_id)
    if student.role != student.Role.STUDENT or student.is_superuser:
        raise PermissionDenied
    if not opportunity.is_open:
        raise ValidationError("Applications are closed for this opportunity.")
    application = (
        Application.objects.select_for_update()
        .filter(student=student, opportunity=opportunity)
        .first()
    )
    if application:
        if application.status == Application.Status.WITHDRAWN:
            application.status = Application.Status.APPLIED
            application.applied_at = application.status_changed_at = timezone.now()
            application.save(update_fields=["status", "applied_at", "status_changed_at"])
            return application, True
        if application.status == Application.Status.REJECTED:
            raise ValidationError("Rejected applications cannot be resubmitted.")
        return application, False
    try:
        with transaction.atomic():
            return Application.objects.create(student=student, opportunity=opportunity), True
    except IntegrityError:
        return Application.objects.get(student=student, opportunity=opportunity), False


@transaction.atomic
def withdraw_application(student, application_id):
    if student.role != student.Role.STUDENT or student.is_superuser:
        raise PermissionDenied
    application = (
        Application.objects.select_for_update()
        .select_related("opportunity")
        .get(pk=application_id, student=student, opportunity__is_removed=False)
    )
    if application.status not in (Application.Status.APPLIED, Application.Status.SHORTLISTED):
        raise ValidationError("This application cannot be withdrawn.")
    application.status = Application.Status.WITHDRAWN
    application.status_changed_at = timezone.now()
    application.save(update_fields=["status", "status_changed_at"])
    return application


@transaction.atomic
def decide_application(faculty, application_id, status):
    if faculty.role != faculty.Role.FACULTY or faculty.is_superuser:
        raise PermissionDenied
    application = (
        Application.objects.select_for_update()
        .select_related("opportunity")
        .get(pk=application_id, opportunity__faculty=faculty, opportunity__is_removed=False)
    )
    if status not in (Application.Status.SHORTLISTED, Application.Status.REJECTED):
        raise ValidationError("Invalid decision.")
    if application.status not in (
        Application.Status.APPLIED,
        Application.Status.SHORTLISTED,
        Application.Status.REJECTED,
    ):
        raise ValidationError("A withdrawn application cannot be changed.")
    if application.status != status:
        application.status = status
        application.status_changed_at = timezone.now()
        application.save(update_fields=["status", "status_changed_at"])
        Notification.objects.create(
            recipient=application.student,
            application=application,
            message=f"Your application for {application.opportunity.title} was {status}.",
        )
    return application
