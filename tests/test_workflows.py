from datetime import date, timedelta

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.urls import reverse

from accounts.models import Opportunity, RequiredSkill, Skill, StudentProfile, StudentSkill, User


@pytest.mark.django_db
def test_registration_login_and_role_escalation(client):
    response = client.post(
        reverse("register"),
        {
            "username": "learner",
            "first_name": "Lee",
            "last_name": "Example",
            "email": "lee@example.com",
            "role": "student",
            "password1": "long-unique-password-573!",
            "password2": "long-unique-password-573!",
            "is_superuser": "on",
        },
    )
    assert response.status_code == 302
    user = User.objects.get(username="learner")
    assert user.role == "student" and not user.is_superuser
    assert StudentProfile.objects.filter(user=user).exists()
    assert client.post(reverse("logout")).status_code == 302
    assert (
        client.post(
            reverse("login"), {"username": "learner", "password": "long-unique-password-573!"}
        ).status_code
        == 302
    )
    response = client.post(reverse("register"), {})
    assert response.status_code == 302


@pytest.mark.django_db
def test_student_portfolio_and_ownership(client):
    student = User.objects.create_user("student", password="password", role="student")
    other = User.objects.create_user("other", password="password", role="student")
    skill = Skill.objects.create(name="Python")
    foreign = StudentSkill.objects.create(student=other, skill=skill, proficiency=2)
    client.force_login(student)
    assert (
        client.post(
            reverse("profile_edit"),
            {"branch": "Computing", "academic_year": 3, "interests": "Research"},
        ).status_code
        == 302
    )
    assert StudentProfile.objects.get(user=student).branch == "Computing"
    assert client.get(reverse("student_edit", args=["skills", foreign.pk])).status_code == 404
    assert (
        client.post(
            reverse("student_add", args=["skills"]), {"skill": skill.pk, "proficiency": 4}
        ).status_code
        == 302
    )
    assert (
        client.post(
            reverse("student_add", args=["skills"]), {"skill": skill.pk, "proficiency": 4}
        ).status_code
        == 200
    )
    assert (
        client.post(
            reverse("student_add", args=["skills"]), {"skill": skill.pk, "proficiency": 5}
        ).status_code
        == 200
    )
    assert (
        client.post(
            reverse("student_add", args=["projects"]), {"title": "Demo", "description": "Work"}
        ).status_code
        == 302
    )
    assert (
        client.post(
            reverse("student_add", args=["certifications"]),
            {"title": "Course", "issuer": "Example"},
        ).status_code
        == 302
    )
    assert client.get(reverse("dashboard")).status_code == 200
    assert client.get(reverse("student_delete", args=["skills", foreign.pk])).status_code == 405


@pytest.mark.django_db
def test_faculty_requirements_and_ownership(client):
    faculty = User.objects.create_user("faculty", role="faculty")
    other = User.objects.create_user("other", role="faculty")
    skill = Skill.objects.create(name="Python")
    client.force_login(faculty)
    response = client.post(
        reverse("opportunity_add"),
        {
            "title": "Research",
            "description": "Description",
            "type": "research",
            "deadline": date.today() + timedelta(days=30),
            "status": "published",
        },
    )
    assert response.status_code == 302
    opportunity = Opportunity.objects.get(faculty=faculty)
    assert client.get(reverse("opportunity_detail", args=[opportunity.pk])).status_code == 200
    url = reverse("requirement_add", args=[opportunity.pk])
    assert (
        client.post(url, {"skill": skill.pk, "minimum_proficiency": 2, "weight": 5}).status_code
        == 302
    )
    assert (
        client.post(url, {"skill": skill.pk, "minimum_proficiency": 2, "weight": 5}).status_code
        == 200
    )
    assert (
        client.post(url, {"skill": skill.pk, "minimum_proficiency": 5, "weight": 0}).status_code
        == 200
    )
    client.force_login(other)
    assert client.get(reverse("opportunity_detail", args=[opportunity.pk])).status_code == 404
    assert client.post(reverse("opportunity_delete", args=[opportunity.pk])).status_code == 404
    assert RequiredSkill.objects.count() == 1


@pytest.mark.django_db
def test_admin_catalogue_and_constraints(client):
    admin = User.objects.create_superuser("admin", "admin@example.com", "password")
    student = User.objects.create_user("student", role="student")
    client.force_login(student)
    assert client.get(reverse("catalogue_add")).status_code == 403
    client.force_login(admin)
    assert (
        client.post(reverse("catalogue_add"), {"name": "Python", "active": "on"}).status_code == 302
    )
    assert (
        client.post(reverse("catalogue_add"), {"name": "python", "active": "on"}).status_code == 200
    )
    skill = Skill.objects.get(name="Python")
    assert (
        client.post(reverse("catalogue_edit", args=[skill.pk]), {"name": "Python"}).status_code
        == 302
    )
    skill.refresh_from_db()
    assert not skill.active
    with pytest.raises(IntegrityError), transaction.atomic():
        Skill.objects.create(name="PYTHON")
    with pytest.raises(IntegrityError), transaction.atomic():
        StudentSkill.objects.create(student=student, skill=skill, proficiency=0)


@pytest.mark.django_db
def test_seed_is_guarded_and_repeatable(monkeypatch):
    monkeypatch.delenv("SKILLBRIDGE_ALLOW_DEMO_SEED", raising=False)
    with pytest.raises(CommandError):
        call_command("seed_demo")
    monkeypatch.setenv("SKILLBRIDGE_ALLOW_DEMO_SEED", "1")
    monkeypatch.setenv("SKILLBRIDGE_DEMO_PASSWORD", "local-test-password-123")
    call_command("seed_demo")
    counts = (User.objects.count(), Skill.objects.count(), Opportunity.objects.count())
    call_command("seed_demo")
    assert counts == (16, 28, 9)
    assert counts == (User.objects.count(), Skill.objects.count(), Opportunity.objects.count())


@pytest.mark.django_db
def test_edit_and_remove_sprint_one_records(client):
    student = User.objects.create_user("student", role="student")
    faculty = User.objects.create_user("faculty", role="faculty")
    admin = User.objects.create_superuser("admin", "admin@example.com", "password")
    skill = Skill.objects.create(name="Python")
    client.force_login(student)
    client.post(reverse("student_add", args=["skills"]), {"skill": skill.pk, "proficiency": 1})
    student_skill = student.student_skills.get()
    assert (
        client.post(
            reverse("student_edit", args=["skills", student_skill.pk]),
            {"skill": skill.pk, "proficiency": 3},
        ).status_code
        == 302
    )
    student_skill.refresh_from_db()
    assert student_skill.proficiency == 3
    for kind, payload, changed in [
        (
            "projects",
            {"title": "First", "description": "Work"},
            {"title": "Revised", "description": "Work"},
        ),
        (
            "certifications",
            {"title": "First", "issuer": "Example"},
            {"title": "Revised", "issuer": "Example"},
        ),
    ]:
        assert client.post(reverse("student_add", args=[kind]), payload).status_code == 302
        obj = getattr(student, kind).get()
        assert client.post(reverse("student_edit", args=[kind, obj.pk]), changed).status_code == 302
        obj.refresh_from_db()
        assert obj.title == "Revised"
        assert client.post(reverse("student_delete", args=[kind, obj.pk])).status_code == 302
        assert not getattr(student, kind).exists()
    assert (
        client.post(reverse("student_delete", args=["skills", student_skill.pk])).status_code == 302
    )
    client.force_login(faculty)
    opportunity = Opportunity.objects.create(
        faculty=faculty,
        title="Initial",
        description="Work",
        type="project",
        deadline=date.today() + timedelta(days=30),
        status="draft",
    )
    updated = {
        "title": "Updated",
        "description": "Work",
        "type": "research",
        "deadline": date.today() + timedelta(days=60),
        "status": "published",
    }
    assert (
        client.post(reverse("opportunity_edit", args=[opportunity.pk]), updated).status_code == 302
    )
    opportunity.refresh_from_db()
    assert opportunity.title == "Updated" and opportunity.status == "published"
    requirement = RequiredSkill.objects.create(
        opportunity=opportunity, skill=skill, minimum_proficiency=1, weight=1
    )
    assert (
        client.post(
            reverse("requirement_edit", args=[opportunity.pk, requirement.pk]),
            {"skill": skill.pk, "minimum_proficiency": 4, "weight": 10},
        ).status_code
        == 302
    )
    requirement.refresh_from_db()
    assert (requirement.minimum_proficiency, requirement.weight) == (4, 10)
    assert (
        client.post(
            reverse("requirement_delete", args=[opportunity.pk, requirement.pk])
        ).status_code
        == 302
    )
    assert not RequiredSkill.objects.filter(pk=requirement.pk).exists()
    assert client.post(reverse("opportunity_delete", args=[opportunity.pk])).status_code == 302
    assert not Opportunity.objects.filter(pk=opportunity.pk).exists()
    client.force_login(admin)
    assert (
        client.post(
            reverse("catalogue_edit", args=[skill.pk]), {"name": "Python 3", "active": "on"}
        ).status_code
        == 302
    )
    skill.refresh_from_db()
    assert skill.name == "Python 3"


@pytest.mark.django_db
def test_faculty_registration_and_invalid_role(client):
    data = {
        "username": "faculty",
        "first_name": "Faculty",
        "last_name": "Example",
        "email": "faculty@example.com",
        "role": "faculty",
        "password1": "long-unique-password-573!",
        "password2": "long-unique-password-573!",
    }
    assert client.post(reverse("register"), data).status_code == 302
    assert User.objects.get(username="faculty").role == "faculty"
    client.post(reverse("logout"))
    data.update(username="intruder", role="admin")
    assert client.post(reverse("register"), data).status_code == 200
    assert not User.objects.filter(username="intruder").exists()
