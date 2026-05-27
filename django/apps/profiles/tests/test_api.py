"""API tests for the profiles app."""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.profiles.models import Student


@pytest.fixture
def api_client(db):
    user = User.objects.create_user(username="doris", password="secret")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestStudentByEmail:
    def test_found(self, api_client):
        Student.objects.create(
            name="Jeremías",
            email="jeremias@test.com",
            priority_areas="vocabulary, grammar",
        )
        resp = api_client.get("/api/students/by-email/", {"email": "jeremias@test.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "jeremias@test.com"
        assert data["priority_areas"] == ["vocabulary", "grammar"]

    def test_not_found(self, api_client):
        resp = api_client.get("/api/students/by-email/", {"email": "missing@test.com"})
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"

    def test_missing_email_param(self, api_client):
        resp = api_client.get("/api/students/by-email/")
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_requires_authentication(self):
        resp = APIClient().get("/api/students/by-email/", {"email": "x@test.com"})
        assert resp.status_code == 401
