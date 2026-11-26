from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from accounts.models import Application, Notification, Opportunity, User
from accounts.services import apply_to_opportunity, decide_application, withdraw_application


@pytest.mark.django_db
def test_withdraw_reapply_decisions_and_notification_ownership(client):
    student = User.objects.create_user("student", role="student")
    stranger = User.objects.create_user("stranger", role="student")
    faculty = User.objects.create_user("faculty", role="faculty")
    other = User.objects.create_user("other", role="faculty")
    opportunity = Opportunity.objects.create(
        faculty=faculty,
        title="Project",
        description="Work",
        type="project",
        deadline=timezone.localdate() + timedelta(days=3),
        status="published",
    )
    application, created = apply_to_opportunity(student, opportunity.pk)
    assert created
    decide_application(faculty, application.pk, Application.Status.SHORTLISTED)
    assert Notification.objects.filter(recipient=student).count() == 1
    client.force_login(stranger)
    assert client.post(reverse("application_withdraw", args=[application.pk])).status_code == 404
    notification = Notification.objects.get(recipient=student)
    assert client.post(reverse("notification_read", args=[notification.pk])).status_code == 404
    client.force_login(other)
    assert (
        client.post(
            reverse("application_decision", args=[application.pk]), {"status": "rejected"}
        ).status_code
        == 404
    )
    withdraw_application(student, application.pk)
    same, created = apply_to_opportunity(student, opportunity.pk)
    assert created and same.pk == application.pk and same.status == Application.Status.APPLIED
    decide_application(faculty, application.pk, Application.Status.REJECTED)
    with pytest.raises(ValidationError):
        withdraw_application(student, application.pk)
    with pytest.raises(ValidationError):
        apply_to_opportunity(student, opportunity.pk)
    assert Notification.objects.filter(recipient=student).count() == 2


@pytest.mark.django_db
def test_removed_and_hard_delete_preserve_application(client):
    student = User.objects.create_user("student", role="student")
    faculty = User.objects.create_user("faculty", role="faculty")
    opportunity = Opportunity.objects.create(
        faculty=faculty,
        title="Project",
        description="Work",
        type="project",
        deadline=timezone.localdate() + timedelta(days=3),
        status="published",
    )
    application = Application.objects.create(student=student, opportunity=opportunity)
    client.force_login(faculty)
    assert client.post(reverse("opportunity_delete", args=[opportunity.pk])).status_code == 302
    assert Opportunity.objects.filter(pk=opportunity.pk).exists()
    opportunity.is_removed = True
    opportunity.save(update_fields=["is_removed"])
    for name in (
        "opportunity_detail",
        "opportunity_edit",
        "opportunity_applicants",
        "requirement_add",
    ):
        assert client.get(reverse(name, args=[opportunity.pk])).status_code == 404
    assert client.post(reverse("opportunity_delete", args=[opportunity.pk])).status_code == 404
    client.force_login(student)
    assert client.post(reverse("opportunity_apply", args=[opportunity.pk])).status_code == 404
    history = client.get(reverse("my_applications"))
    assert b"Removed by administrator" in history.content
    assert reverse("opportunity_detail", args=[opportunity.pk]).encode() not in history.content
    assert Application.objects.filter(pk=application.pk).exists()


@pytest.mark.django_db
def test_team_gap_rejects_ineligible_ids_and_internships(client):
    owner = User.objects.create_user("owner", role="faculty")
    other = User.objects.create_user("other", role="faculty")
    student = User.objects.create_user("student", role="student")
    foreign = User.objects.create_user("foreign", role="student")
    base = {
        "faculty": owner,
        "description": "Work",
        "deadline": timezone.localdate() + timedelta(days=3),
        "status": "published",
    }
    opportunity = Opportunity.objects.create(title="Project", type="project", **base)
    internship = Opportunity.objects.create(title="Internship", type="internship", **base)
    application = Application.objects.create(student=student, opportunity=opportunity)
    client.force_login(owner)
    url = reverse("team_gap", args=[opportunity.pk])
    assert client.get(url, {"selection": "1", "member": student.pk}).status_code == 200
    assert client.get(url, {"selection": "1", "member": foreign.pk}).status_code == 400
    assert client.get(url, {"selection": "1", "member": "bad"}).status_code == 400
    assert client.get(url, {"selection": "1", "member": "9" * 5000}).status_code == 400
    assert client.get(reverse("team_gap", args=[internship.pk])).status_code == 404
    withdraw_application(student, application.pk)
    assert client.get(url, {"selection": "1", "member": student.pk}).status_code == 400
    client.force_login(other)
    assert client.get(url).status_code == 404
