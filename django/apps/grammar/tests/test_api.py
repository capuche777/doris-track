"""API tests for the grammar app."""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.grammar.models import Correction
from apps.profiles.models import Student


@pytest.fixture
def api_client(db):
    user = User.objects.create_user(username="doris", password="secret")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def student(db):
    return Student.objects.create(name="Jeremías", email="jeremias@test.com")


@pytest.mark.django_db
class TestCorrectionCreate:
    def test_create(self, api_client, student):
        payload = {
            "student_mistake": "I didn't remembered the word",
            "correct_version": "I didn't remember the word",
            "grammar_rule": "Use the base form after 'didn't'",
            "category": "verb_tenses",
        }
        resp = api_client.post(
            f"/api/students/{student.id}/corrections/", payload, format="json"
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["category"] == "verb_tenses"
        assert data["student"] == student.id
        assert Correction.objects.filter(student=student).count() == 1

    def test_invalid_category(self, api_client, student):
        payload = {
            "student_mistake": "x",
            "correct_version": "y",
            "category": "nonsense",
        }
        resp = api_client.post(
            f"/api/students/{student.id}/corrections/", payload, format="json"
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_student_not_found(self, api_client):
        payload = {"student_mistake": "x", "correct_version": "y"}
        resp = api_client.post(
            "/api/students/999/corrections/", payload, format="json"
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"

    def test_requires_authentication(self, student):
        resp = APIClient().post(
            f"/api/students/{student.id}/corrections/", {}, format="json"
        )
        assert resp.status_code == 401
