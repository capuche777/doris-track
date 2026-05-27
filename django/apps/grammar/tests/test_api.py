"""API tests for the grammar app."""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.grammar.models import Correction
from apps.grammar.services import log_correction
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


@pytest.mark.django_db
class TestCorrectionList:
    def test_list_and_filter(self, api_client, student):
        log_correction(student, "a", "b", category="verb_tenses")
        log_correction(student, "c", "d", category="articles")
        resp = api_client.get(f"/api/students/{student.id}/corrections/")
        assert resp.status_code == 200
        assert len(resp.json()["corrections"]) == 2

        resp = api_client.get(
            f"/api/students/{student.id}/corrections/", {"category": "articles"}
        )
        corrections = resp.json()["corrections"]
        assert len(corrections) == 1
        assert corrections[0]["category"] == "articles"

    def test_invalid_date_filter(self, api_client, student):
        resp = api_client.get(
            f"/api/students/{student.id}/corrections/", {"date_from": "not-a-date"}
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
class TestCorrectionAnalytics:
    def test_common_mistakes(self, api_client, student):
        log_correction(student, "a", "b", category="prepositions")
        log_correction(student, "c", "d", category="prepositions")
        log_correction(student, "e", "f", category="articles")
        resp = api_client.get(f"/api/students/{student.id}/corrections/analytics/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["period_days"] == 30
        top = data["categories"][0]
        assert top["category"] == "prepositions"
        assert top["count"] == 2


@pytest.mark.django_db
class TestCorrectionTrend:
    def test_trend(self, api_client, student):
        log_correction(student, "a", "b", category="prepositions")
        resp = api_client.get(
            f"/api/students/{student.id}/corrections/trend/prepositions/"
        )
        assert resp.status_code == 200
        assert resp.json()["category"] == "prepositions"

    def test_invalid_category(self, api_client, student):
        resp = api_client.get(
            f"/api/students/{student.id}/corrections/trend/bogus/"
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
