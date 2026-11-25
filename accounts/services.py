"""Transactional application lifecycle operations."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Application, Notification, Opportunity


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
        ("At least three skills", skills_count >= 3, "skills"),
        ("At least one project", projects_count >= 1, "projects"),
        ("At least one certification", certifications_count >= 1, "certifications"),
    )
    return {"score": 20 * sum(item[1] for item in checklist), "checklist": checklist}


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
