"""API tests for the scores app."""
from datetime import date, timedelta

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.profiles.models import Student
from apps.scores.services import record_assessment


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
class TestAssessmentCreate:
    def test_create(self, api_client, student):
        payload = {
            "scores": {"grammar": 76, "vocabulary": 67},
            "assessment_date": "2026-05-27",
            "notes": "May check",
        }
        resp = api_client.post(
            f"/api/students/{student.id}/assessments/", payload, format="json"
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["scores"] == {"grammar": 76, "vocabulary": 67}
        assert data["notes"] == "May check"

    def test_invalid_skill(self, api_client, student):
        payload = {"scores": {"bogus": 50}, "assessment_date": "2026-05-27"}
        resp = api_client.post(
            f"/api/students/{student.id}/assessments/", payload, format="json"
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_value_out_of_range(self, api_client, student):
        payload = {"scores": {"grammar": 150}, "assessment_date": "2026-05-27"}
        resp = api_client.post(
            f"/api/students/{student.id}/assessments/", payload, format="json"
        )
        assert resp.status_code == 400

    def test_student_not_found(self, api_client):
        payload = {"scores": {"grammar": 70}, "assessment_date": "2026-05-27"}
        resp = api_client.post("/api/students/999/assessments/", payload, format="json")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"


@pytest.mark.django_db
class TestScoreReads:
    def test_history_and_skill_filter(self, api_client, student):
        record_assessment(student.id, {"grammar": 70, "fluency": 60}, date.today())
        resp = api_client.get(f"/api/students/{student.id}/scores/")
        assert resp.status_code == 200
        assert resp.json()["scores"][0]["scores"] == {"grammar": 70, "fluency": 60}

        resp = api_client.get(
            f"/api/students/{student.id}/scores/", {"skill": "grammar"}
        )
        assert resp.json()["scores"][0]["scores"] == {"grammar": 70}

    def test_invalid_skill_filter(self, api_client, student):
        resp = api_client.get(f"/api/students/{student.id}/scores/", {"skill": "nope"})
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_latest(self, api_client, student):
        record_assessment(student.id, {"grammar": 70}, date.today() - timedelta(days=2))
        record_assessment(student.id, {"grammar": 80}, date.today())
        resp = api_client.get(f"/api/students/{student.id}/scores/latest/")
        assert resp.status_code == 200
        assert resp.json()["grammar"] == 80

    def test_declining(self, api_client, student):
        record_assessment(student.id, {"grammar": 80}, date.today() - timedelta(days=8))
        record_assessment(student.id, {"grammar": 70}, date.today())
        resp = api_client.get(f"/api/students/{student.id}/scores/declining/")
        assert resp.status_code == 200
        assert "grammar" in resp.json()["declining"]
