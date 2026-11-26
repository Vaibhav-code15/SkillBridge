from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import Opportunity, StudentProfile, User
from accounts.private_files import MAX_RESUME_BYTES, validate_pdf
from accounts.services import (
    apply_to_opportunity,
    remove_profile_resume,
    replace_profile_resume,
    withdraw_application,
)


def pdf(name="resume.pdf", data=b"%PDF-1.4\nfictional\n%%EOF\n"):
    return SimpleUploadedFile(name, data, content_type="application/octet-stream")


@pytest.mark.parametrize(
    "name,data",
    [
        ("bad.txt", b"%PDF-1.4\n%%EOF"),
        ("bad.pdf", b""),
        ("bad.pdf", b"wrong\n%%EOF"),
        ("bad.pdf", b"%PDF-1.4\nmissing"),
        ("bad.pdf", b"%PDF-" + b"x" * MAX_RESUME_BYTES + b"%%EOF"),
    ],
)
def test_invalid_resume_rejected(name, data):
    with pytest.raises(ValidationError):
        validate_pdf(pdf(name, data))


@pytest.mark.django_db(transaction=True)
def test_private_snapshot_and_permissions(settings, tmp_path):
    settings.PRIVATE_MEDIA_ROOT = tmp_path
    student = User.objects.create_user("student", role="student")
    other = User.objects.create_user("other", role="student")
    faculty = User.objects.create_user("faculty", role="faculty")
    other_faculty = User.objects.create_user("otherfaculty", role="faculty")
    admin = User.objects.create_superuser("admin", "admin@example.com", "password")
    profile = StudentProfile.objects.create(user=student)
    opportunity = Opportunity.objects.create(
        faculty=faculty,
        title="Research",
        description="Work",
        type="research",
        deadline=timezone.localdate() + timedelta(days=10),
        status="published",
    )
    replace_profile_resume(student, pdf())
    profile.refresh_from_db()
    original_profile_name = profile.resume.name
    profile_url = reverse("profile_resume_download")
    profile_client = Client()
    assert profile_client.get(profile_url).status_code == 404
    profile_client.force_login(other)
    assert profile_client.get(profile_url).status_code == 404
    profile_client.force_login(student)
    own_profile_response = profile_client.get(profile_url)
    assert own_profile_response.status_code == 200
    own_profile_response.close()
    application, created = apply_to_opportunity(
        student, opportunity.pk, note="  Hello <script>  ", use_profile_resume=True
    )
    assert created and application.note == "Hello <script>"
    snapshot = application.resume.name
    assert snapshot != original_profile_name
    assert (tmp_path / snapshot).exists()
    replace_profile_resume(student, pdf("replacement.pdf"))
    remove_profile_resume(student)
    assert not (tmp_path / original_profile_name).exists()
    assert (tmp_path / snapshot).exists()
    client = Client()
    url = reverse("application_resume_download", args=[application.pk])
    assert client.get(url).status_code == 404
    for user in [other, other_faculty, admin]:
        client.force_login(user)
        assert client.get(url).status_code == 404
    for user in [student, faculty]:
        client.force_login(user)
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert response["X-Content-Type-Options"] == "nosniff"
        assert response["Cache-Control"] == "private, no-store"
        assert "attachment" in response["Content-Disposition"]
        response.close()
    withdraw_application(student, application.pk)
    client.force_login(faculty)
    assert client.get(url).status_code == 404
    client.force_login(student)
    own_response = client.get(url)
    assert own_response.status_code == 200
    own_response.close()
    application, created = apply_to_opportunity(
        student, opportunity.pk, note="New note", resume=pdf("other.pdf")
    )
    assert created and application.note == "New note" and application.resume.name != snapshot
    assert not (tmp_path / snapshot).exists()
    opportunity.is_removed = True
    opportunity.save(update_fields=["is_removed"])
    client.force_login(faculty)
    assert client.get(url).status_code == 404
    client.force_login(student)
    own_response = client.get(url)
    assert own_response.status_code == 200
    own_response.close()


@pytest.mark.django_db
def test_note_length_validation():
    student = User.objects.create_user("student", role="student")
    faculty = User.objects.create_user("faculty", role="faculty")
    opportunity = Opportunity.objects.create(
        faculty=faculty,
        title="Research",
        description="Work",
        type="research",
        deadline=timezone.localdate() + timedelta(days=10),
        status="published",
    )
    with pytest.raises(ValidationError):
        apply_to_opportunity(student, opportunity.pk, note="x" * 1501)
