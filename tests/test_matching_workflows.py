from datetime import date, datetime, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import (
    Application,
    Certification,
    Opportunity,
    Project,
    RequiredSkill,
    Skill,
    StudentProfile,
    StudentSkill,
    User,
)


def make_opportunity(faculty, *, title, kind="research", status="published", deadline=None):
    return Opportunity.objects.create(
        faculty=faculty,
        title=title,
        description="Academic work for students",
        type=kind,
        status=status,
        deadline=deadline or timezone.localdate() + timedelta(days=10),
    )


@pytest.mark.django_db
def test_search_filters_and_pagination_keep_query_state(client):
    student = User.objects.create_user("student", password="password", role="student")
    faculty = User.objects.create_user("faculty", role="faculty")
    python = Skill.objects.create(name="Python")
    python_web = Skill.objects.create(name="Python Web Development")
    for index in range(10):
        item = make_opportunity(faculty, title=f"Campus Project {index}", kind="project")
        RequiredSkill.objects.create(
            opportunity=item, skill=python, minimum_proficiency=2, weight=3
        )
        RequiredSkill.objects.create(
            opportunity=item, skill=python_web, minimum_proficiency=2, weight=2
        )
    make_opportunity(faculty, title="Unrelated research", kind="research")
    client.force_login(student)

    response = client.get(
        reverse("opportunity_list"), {"q": "  pYtHoN  ", "type": "project", "skill": python.pk}
    )

    assert response.status_code == 200
    assert response.context["search"] == "pYtHoN"
    assert response.context["page_obj"].paginator.count == 10
    assert len(response.context["page_obj"]) == 9
    assert all(item.match_result.score == 0 for item in response.context["page_obj"])
    next_url = response.context["page_obj"].next_page_number()
    html = response.content.decode()
    assert f"q=pYtHoN&amp;type=project&amp;skill={python.pk}&amp;page={next_url}" in html
    empty = client.get(reverse("opportunity_list"), {"q": "nothing matches"})
    assert b"No opportunities found" in empty.content


@pytest.mark.django_db
def test_application_post_guards_duplicates_closed_draft_roles_and_csrf(client):
    student = User.objects.create_user("student", password="password", role="student")
    faculty = User.objects.create_user("faculty", password="password", role="faculty")
    open_item = make_opportunity(faculty, title="Open research")
    closed_item = make_opportunity(faculty, title="Closed research", status="closed")
    expired = make_opportunity(
        faculty, title="Expired research", deadline=timezone.localdate() - timedelta(days=1)
    )
    draft = make_opportunity(faculty, title="Draft research", status="draft")
    apply_url = reverse("opportunity_apply", args=[open_item.pk])

    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(student)
    assert csrf_client.post(apply_url).status_code == 403
    assert Application.objects.count() == 0

    client.force_login(student)
    assert client.get(apply_url).status_code == 405
    assert client.post(apply_url).status_code == 302
    assert client.post(apply_url).status_code == 302
    for item in (closed_item, expired):
        assert client.post(reverse("opportunity_apply", args=[item.pk])).status_code == 302
    assert client.post(reverse("opportunity_apply", args=[draft.pk])).status_code == 404
    assert Application.objects.filter(student=student, opportunity=open_item).count() == 1
    assert Application.objects.count() == 1
    applied_detail = client.get(reverse("opportunity_detail", args=[open_item.pk]))
    assert b"Applied on" in applied_detail.content

    client.force_login(faculty)
    assert client.post(apply_url).status_code == 403

    client.force_login(student)
    response = client.get(reverse("opportunity_detail", args=[expired.pk]))
    assert response.status_code == 200
    assert b"Applications closed" in response.content
    assert (
        b"Applications closed"
        in client.get(reverse("opportunity_detail", args=[closed_item.pk])).content
    )
    assert client.get(reverse("opportunity_detail", args=[draft.pk])).status_code == 404


@pytest.mark.django_db
def test_open_boundary_uses_local_date_for_property_and_queryset(client, monkeypatch):
    today = date(2026, 11, 25)
    monkeypatch.setattr("accounts.models.timezone.localdate", lambda: today)
    faculty = User.objects.create_user("faculty", role="faculty")
    due_today = make_opportunity(faculty, title="Due today", deadline=today)
    expired = make_opportunity(faculty, title="Past", deadline=today - timedelta(days=1))
    closed = make_opportunity(faculty, title="Closed", status="closed", deadline=today)

    due_today.refresh_from_db()
    expired.refresh_from_db()
    assert due_today.is_open
    assert not expired.is_open
    assert not closed.is_open
    assert list(Opportunity.objects.is_open()) == [due_today]


@pytest.mark.django_db
def test_faculty_browse_excludes_other_faculty_opportunities(client):
    owner = User.objects.create_user("owner", role="faculty")
    other = User.objects.create_user("other", role="faculty")
    own = make_opportunity(owner, title="My opportunity")
    foreign = make_opportunity(other, title="Another opportunity")
    client.force_login(owner)
    response = client.get(reverse("opportunity_list"))
    assert response.status_code == 200
    assert list(response.context["page_obj"]) == [own]
    assert client.get(reverse("opportunity_detail", args=[own.pk])).status_code == 200
    assert client.get(reverse("opportunity_detail", args=[foreign.pk])).status_code == 404
    assert client.get(reverse("opportunity_applicants", args=[foreign.pk])).status_code == 404
    assert client.get(reverse("opportunity_edit", args=[foreign.pk])).status_code == 404
    assert client.post(reverse("opportunity_delete", args=[foreign.pk])).status_code == 404
    assert Opportunity.objects.filter(pk=foreign.pk).exists()


@pytest.mark.django_db
def test_applicants_are_ranked_live_and_other_roles_cannot_view(client):
    faculty = User.objects.create_user("faculty", password="password", role="faculty")
    other_faculty = User.objects.create_user("other", password="password", role="faculty")
    student_role = User.objects.create_user("viewer", password="password", role="student")
    item = make_opportunity(faculty, title="Campus data study")
    skill = Skill.objects.create(name="Python")
    RequiredSkill.objects.create(opportunity=item, skill=skill, minimum_proficiency=2, weight=2)

    candidates = []
    for username, first, last, level in [
        ("tie_a", "Alex", "Example", 2),
        ("tie_b", "Alex", "Example", 2),
        ("lower", "Aaron", "Example", 1),
    ]:
        student = User.objects.create_user(
            username, role="student", first_name=first, last_name=last
        )
        StudentProfile.objects.create(
            user=student, branch="Computing", academic_year=3, interests="Data and research"
        )
        StudentSkill.objects.create(student=student, skill=skill, proficiency=level)
        Project.objects.create(student=student, title="Campus dashboard", description="A project")
        Certification.objects.create(student=student, title="Data Foundations", issuer="Example")
        candidates.append(student)

    tied_time = timezone.make_aware(datetime(2026, 10, 1, 12))
    for student in candidates[:2]:
        Application.objects.create(student=student, opportunity=item, applied_at=tied_time)

    client.force_login(candidates[2])
    discovery = client.get(
        reverse("opportunity_list"), {"q": "campus data", "type": "research", "skill": skill.pk}
    )
    assert discovery.status_code == 200
    assert discovery.context["page_obj"].paginator.count == 1
    detail = client.get(reverse("opportunity_detail", args=[item.pk]))
    assert detail.status_code == 200
    assert detail.context["fit"].score == 50
    apply_url = reverse("opportunity_apply", args=[item.pk])
    assert client.post(apply_url).status_code == 302
    assert client.post(apply_url).status_code == 302
    assert Application.objects.filter(student=candidates[2], opportunity=item).count() == 1

    client.force_login(faculty)
    response = client.get(reverse("opportunity_applicants", args=[item.pk]))
    assert response.status_code == 200
    ranked = response.context["applicants"]
    assert [application.student.username for application in ranked] == ["tie_a", "tie_b", "lower"]
    assert [application.match_result.score for application in ranked] == [100, 100, 50]
    assert all(application.rank == rank for rank, application in enumerate(ranked, start=1))
    assert b"Campus dashboard" in response.content
    assert b"Data Foundations" in response.content

    client.force_login(other_faculty)
    assert client.get(reverse("opportunity_applicants", args=[item.pk])).status_code == 404
    client.force_login(student_role)
    assert client.get(reverse("opportunity_applicants", args=[item.pk])).status_code == 403


@pytest.mark.django_db
def test_detail_shows_fit_to_students_and_requirements_only_to_faculty(client):
    student = User.objects.create_user("student", password="password", role="student")
    faculty = User.objects.create_user("faculty", password="password", role="faculty")
    item = make_opportunity(faculty, title="Research placement")
    skill = Skill.objects.create(name="Python")
    RequiredSkill.objects.create(opportunity=item, skill=skill, minimum_proficiency=3, weight=4)

    client.force_login(student)
    response = client.get(reverse("opportunity_detail", args=[item.pk]))
    assert response.status_code == 200
    assert response.context["fit"].score is None or response.context["fit"].score == 0
    assert b"Your skill fit" in response.content
    assert b"Minimum 3 / 4" in response.content
    assert b"Add skills to your profile" in response.content
    assert b"Applications closed" not in response.content

    client.force_login(faculty)
    response = client.get(reverse("opportunity_detail", args=[item.pk]))
    assert response.status_code == 200
    assert b"Your skill fit" not in response.content
    assert b"View applicants" in response.content
