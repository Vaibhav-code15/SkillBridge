"""Transactional application lifecycle operations."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from matching.advanced import suggest_improvements

from .matching import match_student, requirements_for, skill_levels_for
from .models import Application, Notification, Opportunity, StudentProfile, User
from .private_files import (
    delete_private_file,
    display_name,
    private_resume_storage,
    resume_path,
    validate_pdf,
)

MIN_PROFILE_SKILLS = 3


@transaction.atomic
def replace_profile_resume(student, upload):
    if student.role != student.Role.STUDENT or student.is_superuser:
        raise PermissionDenied
    validate_pdf(upload)
    profile = StudentProfile.objects.select_for_update().get(user=student)
    old_name = profile.resume.name if profile.resume else ""
    stored = private_resume_storage.save(resume_path(profile, upload.name), upload)
    try:
        profile.resume = stored
        profile.resume_name = display_name(upload.name)
        profile.resume_size = upload.size
        profile.save(update_fields=["resume", "resume_name", "resume_size"])
    except Exception:
        delete_private_file(stored)
        raise
    if old_name:
        transaction.on_commit(lambda: delete_private_file(old_name))
    return profile


@transaction.atomic
def remove_profile_resume(student):
    if student.role != student.Role.STUDENT or student.is_superuser:
        raise PermissionDenied
    profile = StudentProfile.objects.select_for_update().get(user=student)
    old_name = profile.resume.name if profile.resume else ""
    profile.resume = ""
    profile.resume_name = ""
    profile.resume_size = None
    profile.save(update_fields=["resume", "resume_name", "resume_size"])
    if old_name:
        transaction.on_commit(lambda: delete_private_file(old_name))
    return profile


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
def apply_to_opportunity(student, opportunity_id, note="", resume=None, use_profile_resume=False):
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
            pass
        elif application.status == Application.Status.REJECTED:
            raise ValidationError("Rejected applications cannot be resubmitted.")
        else:
            return application, False
    note = (note or "").strip()
    if len(note) > 1500:
        raise ValidationError("The application note must be at most 1,500 characters.")
    if resume and use_profile_resume:
        raise ValidationError("Choose either your profile resume or a new upload.")
    source = resume
    name = display_name(resume.name) if resume else ""
    if use_profile_resume:
        profile = getattr(student, "profile", None)
        if not profile or not profile.resume:
            raise ValidationError("Upload a profile resume before attaching it.")
        try:
            source = profile.resume.open("rb")
            name = profile.resume_name or "resume.pdf"
        except OSError as exc:
            raise ValidationError(
                "Your profile resume is unavailable. Please upload it again."
            ) from exc
    stored = ""
    try:
        if source:
            validate_pdf(source)
            stored = private_resume_storage.save(resume_path(None, name), source)
        old_resume = application.resume.name if application and application.resume else ""
        if application:
            application.status = Application.Status.APPLIED
            application.applied_at = application.status_changed_at = timezone.now()
        else:
            application = Application(student=student, opportunity=opportunity)
        application.note = note
        application.resume = stored
        application.resume_name = name
        application.resume_size = source.size if source else None
        application.full_clean()
        if application.resume:
            application.resume.close()
        try:
            with transaction.atomic():
                application.save()
        except IntegrityError:
            existing = Application.objects.filter(student=student, opportunity=opportunity).first()
            if existing is None:
                raise
            if stored:
                delete_private_file(stored)
                stored = ""
            return existing, False
        if old_resume:
            transaction.on_commit(lambda: delete_private_file(old_resume))
        return application, True
    except Exception:
        if stored:
            delete_private_file(stored)
        raise
    finally:
        if use_profile_resume and source:
            source.close()


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
