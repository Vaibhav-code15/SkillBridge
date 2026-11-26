from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import Application, Opportunity, RequiredSkill, Skill, User


@pytest.mark.django_db
def test_admin_user_moderation_and_inactive_sessions(client):
    admin = User.objects.create_superuser("admin", "admin@example.com", "password")
    other_admin = User.objects.create_superuser("otheradmin", "other@example.com", "password")
    student = User.objects.create_user("student", password="password", role="student")
    active_session = Client()
    active_session.force_login(student)
    client.force_login(student)
    assert client.get(reverse("admin_reports")).status_code == 403
    assert client.get(reverse("moderation")).status_code == 403
    client.force_login(admin)
    assert (
        client.post(reverse("moderate_user", args=[admin.pk]), {"active": "0"}).status_code == 403
    )
    assert (
        client.post(reverse("moderate_user", args=[other_admin.pk]), {"active": "0"}).status_code
        == 403
    )
    assert (
        client.post(reverse("moderate_user", args=[student.pk]), {"active": "0"}).status_code == 302
    )
    assert active_session.get(reverse("dashboard")).status_code == 302
    login = Client().post(reverse("login"), {"username": "student", "password": "password"})
    assert login.status_code == 200 and b"account is inactive" in login.content
    assert (
        client.post(reverse("moderate_user", args=[student.pk]), {"active": "1"}).status_code == 302
    )
    assert Client().login(username="student", password="password")


@pytest.mark.django_db
def test_moderation_removal_reports_and_historical_visibility(client):
    admin = User.objects.create_superuser("admin", "admin@example.com", "password")
    faculty = User.objects.create_user("faculty", role="faculty")
    student = User.objects.create_user("student", role="student")
    item = Opportunity.objects.create(
        faculty=faculty,
        title="Project",
        description="Work",
        type="project",
        deadline=timezone.localdate() + timedelta(days=3),
        status="published",
    )
    skill = Skill.objects.create(name="Python")
    RequiredSkill.objects.create(opportunity=item, skill=skill, minimum_proficiency=2, weight=1)
    Application.objects.create(student=student, opportunity=item)
    client.force_login(admin)
    assert client.get(reverse("admin_reports")).status_code == 200
    assert (
        client.post(reverse("moderate_opportunity", args=[item.pk]), {"removed": "1"}).status_code
        == 302
    )
    reports = client.get(reverse("admin_reports"))
    assert reports.context["removed_count"] == 1
    assert list(reports.context["demanded_skills"]) == []
    client.force_login(faculty)
    for name in (
        "opportunity_detail",
        "opportunity_edit",
        "opportunity_applicants",
        "requirement_add",
        "team_gap",
    ):
        assert client.get(reverse(name, args=[item.pk])).status_code == 404
    client.force_login(student)
    assert client.post(reverse("opportunity_apply", args=[item.pk])).status_code == 404
    assert b"Removed by administrator" in client.get(reverse("my_applications")).content
    assert item.pk not in [
        row.pk for row in client.get(reverse("opportunity_list")).context["page_obj"]
    ]
    assert item.pk not in [
        row.pk for row in client.get(reverse("recommendations")).context["recommendations"]
    ]
    client.force_login(admin)
    assert (
        client.post(reverse("moderate_opportunity", args=[item.pk]), {"removed": "0"}).status_code
        == 302
    )
    item.refresh_from_db()
    assert not item.is_removed and item.removed_at is None
