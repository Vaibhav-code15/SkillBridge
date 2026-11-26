from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.models import Application, Opportunity, RequiredSkill, Skill, StudentSkill, User
from accounts.services import (
    close_expired_opportunities,
    profile_completeness,
    recommend_opportunities,
    student_improvements,
    withdraw_application,
)


def test_completeness_checklist():
    assert profile_completeness("", None, "", 0, 0, 0)["score"] == 0
    assert profile_completeness("Computer Science", 2, "Research", 3, 1, 1)["score"] == 100
    assert profile_completeness("Computer Science", None, "Research", 2, 1, 0)["score"] == 40


@pytest.mark.django_db
def test_close_expired_is_idempotent_and_preserves_deadline_day():
    faculty = User.objects.create_user("faculty", role="faculty")
    today = timezone.localdate()
    base = {"faculty": faculty, "description": "Work", "type": "project", "status": "published"}
    past = Opportunity.objects.create(title="Past", deadline=today - timedelta(days=1), **base)
    due = Opportunity.objects.create(title="Today", deadline=today, **base)
    removed = Opportunity.objects.create(
        title="Removed", deadline=today - timedelta(days=1), is_removed=True, **base
    )
    assert close_expired_opportunities(today) == 1
    assert close_expired_opportunities(today) == 0
    past.refresh_from_db()
    due.refresh_from_db()
    removed.refresh_from_db()
    assert past.status == Opportunity.Status.CLOSED
    assert due.status == Opportunity.Status.PUBLISHED
    assert removed.status == Opportunity.Status.PUBLISHED


@pytest.mark.django_db
def test_recommendations_order_exclusions_and_improvements(client):
    student = User.objects.create_user("student", role="student")
    faculty = User.objects.create_user("faculty", role="faculty")
    skill = Skill.objects.create(name="Python")
    StudentSkill.objects.create(student=student, skill=skill, proficiency=2)
    today = timezone.localdate()
    base = {"faculty": faculty, "description": "Work", "type": "project", "status": "published"}
    later = Opportunity.objects.create(title="Later", deadline=today + timedelta(days=4), **base)
    earlier = Opportunity.objects.create(
        title="Earlier", deadline=today + timedelta(days=3), **base
    )
    active = Opportunity.objects.create(title="Applied", deadline=today + timedelta(days=2), **base)
    removed = Opportunity.objects.create(
        title="Removed", deadline=today + timedelta(days=1), is_removed=True, **base
    )
    for opportunity in (later, earlier, active, removed):
        RequiredSkill.objects.create(
            opportunity=opportunity, skill=skill, minimum_proficiency=4, weight=1
        )
    application = Application.objects.create(student=student, opportunity=active)
    assert [item.pk for item in recommend_opportunities(student, 10)] == [earlier.pk, later.pk]
    withdraw_application(student, application.pk)
    assert [item.pk for item in recommend_opportunities(student, 10)] == [
        active.pk,
        earlier.pk,
        later.pk,
    ]
    suggestions = student_improvements(student)
    assert suggestions[0]["item"].opportunities_affected == 3
    assert suggestions[0]["gain"] == 150.0
    client.force_login(student)
    assert client.get("/recommendations/").status_code == 200
    assert client.get("/improvements/").status_code == 200
