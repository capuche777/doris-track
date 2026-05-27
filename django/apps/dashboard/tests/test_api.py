"""API tests for the dashboard endpoint."""
from datetime import date

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.grammar.services import log_correction
from apps.practice.services import log_practice
from apps.profiles.models import Student
from apps.scores.services import record_assessment
from apps.vocabulary.models import Word


@pytest.fixture
def api_client(db):
    user = User.objects.create_user(username="doris", password="secret")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def student(db):
    return Student.objects.create(
        name="Jeremías",
        email="jeremias@test.com",
        start_date=date(2025, 5, 1),
        priority_areas="vocabulary, grammar",
    )


@pytest.mark.django_db
class TestDashboard:
    def test_reshaped_snapshot(self, api_client, student):
        record_assessment(student.id, {"grammar": 76}, date.today())
        Word.objects.create(student=student, word="vow", definition="d", times_wrong=2)
        log_practice(student, "vocabulary", 25)
        log_correction(student, "worthy about", "worthy of", category="prepositions")

        resp = api_client.get(f"/api/students/{student.id}/dashboard/")
        assert resp.status_code == 200
        data = resp.json()

        # student_info exposes start_date + priority_areas (as a list)
        assert data["student_info"]["start_date"] == "2025-05-01"
        assert data["student_info"]["priority_areas"] == ["vocabulary", "grammar"]
        # vocabulary_stats uses the API key name
        assert "due_today" in data["vocabulary_stats"]
        # practice_streak is a scalar
        assert data["practice_streak"] == 1
        # difficult_words carry failure_rate; grammar_alerts carry a trend
        assert "failure_rate" in data["difficult_words"][0]
        assert "trend" in data["grammar_alerts"][0]
        # next_quiz_date is a date string
        assert isinstance(data["next_quiz_date"], str)

    def test_student_not_found(self, api_client):
        resp = api_client.get("/api/students/999/dashboard/")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"
