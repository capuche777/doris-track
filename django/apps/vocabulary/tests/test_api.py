"""API tests for the vocabulary app."""
from datetime import date, timedelta

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.profiles.models import Student
from apps.vocabulary.models import Word


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
class TestWordsDue:
    def test_lists_only_due_words(self, api_client, student):
        Word.objects.create(
            student=student, word="vow", definition="a solemn promise",
            next_review_date=date.today(),
        )
        Word.objects.create(
            student=student, word="later", definition="not due yet",
            next_review_date=date.today() + timedelta(days=5),
        )
        resp = api_client.get(f"/api/students/{student.id}/words/due/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert [w["word"] for w in data["words"]] == ["vow"]

    def test_limit_caps_words_but_not_count(self, api_client, student):
        for i in range(5):
            Word.objects.create(
                student=student, word=f"word{i}", definition="d",
                next_review_date=date.today(),
            )
        resp = api_client.get(f"/api/students/{student.id}/words/due/", {"limit": 2})
        data = resp.json()
        assert data["count"] == 5
        assert len(data["words"]) == 2

    def test_student_not_found(self, api_client):
        resp = api_client.get("/api/students/999/words/due/")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"


@pytest.mark.django_db
class TestWordReview:
    def test_correct_answer(self, api_client, student):
        word = Word.objects.create(
            student=student, word="vow", definition="a solemn promise",
            next_review_date=date.today(),
        )
        resp = api_client.post(
            f"/api/words/{word.id}/review/", {"student_answer": "vow"}, format="json"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["correct"] is True
        assert data["correct_answer"] == "vow"
        assert "current_interval_days" in data

    def test_incorrect_answer(self, api_client, student):
        word = Word.objects.create(
            student=student, word="vow", definition="x",
            next_review_date=date.today(),
        )
        resp = api_client.post(
            f"/api/words/{word.id}/review/", {"student_answer": "promise"}, format="json"
        )
        assert resp.status_code == 200
        assert resp.json()["correct"] is False

    def test_empty_answer_is_validation_error(self, api_client, student):
        word = Word.objects.create(student=student, word="vow", definition="x")
        resp = api_client.post(
            f"/api/words/{word.id}/review/", {"student_answer": ""}, format="json"
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_word_not_found(self, api_client):
        resp = api_client.post(
            "/api/words/999/review/", {"student_answer": "x"}, format="json"
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "WORD_NOT_FOUND"
