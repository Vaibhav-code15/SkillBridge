from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.models import Opportunity, User
from accounts.services import close_expired_opportunities, profile_completeness


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
