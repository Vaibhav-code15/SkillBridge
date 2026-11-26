from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import (
    Application,
    Notification,
    Opportunity,
    RequiredSkill,
    Skill,
    StudentSkill,
    User,
)


@pytest.mark.django_db
def test_student_faculty_lifecycle_and_notifications_end_to_end():
    student = User.objects.create_user("learner", password="password", role="student")
    faculty = User.objects.create_user("teacher", password="password", role="faculty")
    item = Opportunity.objects.create(
        faculty=faculty,
        title="Research",
        description="Work",
        type="research",
        deadline=timezone.localdate() + timedelta(days=10),
        status="published",
    )
    skill = Skill.objects.create(name="Python")
    StudentSkill.objects.create(student=student, skill=skill, proficiency=2)
    RequiredSkill.objects.create(opportunity=item, skill=skill, minimum_proficiency=4, weight=1)
    student_client = Client()
    faculty_client = Client()
    assert student_client.login(username="learner", password="password")
    assert faculty_client.login(username="teacher", password="password")
    assert (
        student_client.get(reverse("recommendations")).context["recommendations"][0].pk == item.pk
    )
    assert student_client.post(reverse("opportunity_apply", args=[item.pk])).status_code == 302
    application = Application.objects.get(student=student, opportunity=item)
    assert (
        faculty_client.post(
            reverse("application_decision", args=[application.pk]), {"status": "shortlisted"}
        ).status_code
        == 302
    )
    notification = Notification.objects.get(recipient=student)
    assert student_client.get(reverse("notification_inbox")).status_code == 200
    assert (
        student_client.post(reverse("notification_read", args=[notification.pk])).status_code == 302
    )
    notification.refresh_from_db()
    assert notification.read_at is not None
    team = faculty_client.get(reverse("team_gap", args=[item.pk]))
    assert student.pk in team.context["selected"]
    assert team.context["result"].score == 50
    assert (
        student_client.post(reverse("application_withdraw", args=[application.pk])).status_code
        == 302
    )
    assert student_client.post(reverse("opportunity_apply", args=[item.pk])).status_code == 302
    application.refresh_from_db()
    assert application.status == Application.Status.APPLIED
    assert (
        faculty_client.post(
            reverse("application_decision", args=[application.pk]), {"status": "rejected"}
        ).status_code
        == 302
    )
    assert b"Rejected" in student_client.get(reverse("my_applications")).content
    assert Notification.objects.filter(recipient=student).count() == 2
