import pytest
from django.urls import reverse

from accounts.models import User


@pytest.mark.django_db
def test_public_and_role_pages_have_meaningful_titles(client):
    assert b"Welcome | SkillBridge" in client.get(reverse("home")).content
    assert b"Sign in | SkillBridge" in client.get(reverse("login")).content
    assert b"Create account | SkillBridge" in client.get(reverse("register")).content
    student = User.objects.create_user("student", role="student")
    client.force_login(student)
    for name, title in [
        ("dashboard", "Overview"),
        ("my_applications", "My applications"),
        ("notification_inbox", "Notifications"),
        ("recommendations", "Recommendations"),
    ]:
        assert f"{title} | SkillBridge".encode() in client.get(reverse(name)).content
