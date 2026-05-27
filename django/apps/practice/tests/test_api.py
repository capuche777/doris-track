"""API tests for the practice app."""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.practice.models import PracticeSession
from apps.practice.services import log_practice
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
class TestPracticeCreate:
    def test_log_session(self, api_client, student):
        payload = {
            "practice_type": "vocabulary",
            "duration_minutes": 25,
            "notes": "Reviewed Set 1",
        }
        resp = api_client.post(
            f"/api/students/{student.id}/practice/", payload, format="json"
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["practice_type"] == "vocabulary"
        assert data["duration_minutes"] == 25
        assert PracticeSession.objects.filter(student=student).count() == 1

    def test_invalid_type(self, api_client, student):
        payload = {"practice_type": "bogus", "duration_minutes": 10}
        resp = api_client.post(
            f"/api/students/{student.id}/practice/", payload, format="json"
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_student_not_found(self, api_client):
        payload = {"practice_type": "writing", "duration_minutes": 5}
        resp = api_client.post("/api/students/999/practice/", payload, format="json")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"


@pytest.mark.django_db
class TestPracticeList:
    def test_list(self, api_client, student):
        log_practice(student, "vocabulary", 20)
        log_practice(student, "writing", 30)
        resp = api_client.get(f"/api/students/{student.id}/practice/")
        assert resp.status_code == 200
        assert len(resp.json()["sessions"]) == 2

    def test_filter_by_type(self, api_client, student):
        log_practice(student, "vocabulary", 20)
        log_practice(student, "writing", 30)
        resp = api_client.get(
            f"/api/students/{student.id}/practice/", {"practice_type": "writing"}
        )
        sessions = resp.json()["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["practice_type"] == "writing"


@pytest.mark.django_db
class TestPracticeStreakAndStats:
    def test_streak(self, api_client, student):
        log_practice(student, "vocabulary", 20)
        resp = api_client.get(f"/api/students/{student.id}/practice/streak/")
        assert resp.status_code == 200
        assert resp.json()["streak"] == 1

    def test_stats_by_type_has_sessions_and_minutes(self, api_client, student):
        log_practice(student, "vocabulary", 20)
        log_practice(student, "vocabulary", 10)
        log_practice(student, "writing", 45)
        resp = api_client.get(f"/api/students/{student.id}/practice/stats/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_minutes"] == 75
        assert data["total_sessions"] == 3
        assert data["by_type"]["vocabulary"] == {"sessions": 2, "minutes": 30}
        assert data["by_type"]["writing"] == {"sessions": 1, "minutes": 45}
