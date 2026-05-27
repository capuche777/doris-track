"""API tests for the quiz app."""
from datetime import date

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.profiles.models import Student
from apps.quiz.models import Quiz, QuizQuestion
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
class TestQuizGenerate:
    def test_generates_questions_from_due_words(self, api_client, student):
        Word.objects.create(
            student=student, word="vow", definition="a solemn promise",
            example_sentence="She made a vow.", next_review_date=date.today(),
        )
        resp = api_client.post(f"/api/students/{student.id}/quiz/generate/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_questions"] > 0
        assert "correct_answer" in data["questions"][0]

    def test_idempotent(self, api_client, student):
        Word.objects.create(
            student=student, word="vow", definition="a solemn promise",
            example_sentence="She made a vow.", next_review_date=date.today(),
        )
        first = api_client.post(f"/api/students/{student.id}/quiz/generate/").json()
        second = api_client.post(f"/api/students/{student.id}/quiz/generate/").json()
        assert first["quiz_id"] == second["quiz_id"]

    def test_student_not_found(self, api_client):
        resp = api_client.post("/api/students/999/quiz/generate/")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "STUDENT_NOT_FOUND"


@pytest.mark.django_db
class TestQuizAnswer:
    def _question(self, student):
        quiz = Quiz.objects.create(student=student, week_start_date=date.today())
        return QuizQuestion.objects.create(
            quiz=quiz, question_type="definition_to_word",
            prompt="Definition: a solemn promise", correct_answer="vow",
        )

    def test_correct(self, api_client, student):
        question = self._question(student)
        resp = api_client.post(
            f"/api/questions/{question.id}/answer/",
            {"student_answer": "vow"}, format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["is_correct"] is True

    def test_incorrect(self, api_client, student):
        question = self._question(student)
        resp = api_client.post(
            f"/api/questions/{question.id}/answer/",
            {"student_answer": "promise"}, format="json",
        )
        assert resp.json()["is_correct"] is False

    def test_question_not_found(self, api_client):
        resp = api_client.post(
            "/api/questions/999/answer/", {"student_answer": "x"}, format="json"
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "QUESTION_NOT_FOUND"


@pytest.mark.django_db
class TestQuizListAndResults:
    def test_list_and_results(self, api_client, student):
        quiz = Quiz.objects.create(student=student, week_start_date=date.today())
        QuizQuestion.objects.create(
            quiz=quiz, question_type="definition_to_word",
            prompt="p", correct_answer="vow", is_correct=True,
        )
        resp = api_client.get(f"/api/students/{student.id}/quizzes/")
        assert resp.status_code == 200
        assert resp.json()["quizzes"][0]["quiz_id"] == quiz.id

        resp = api_client.get(f"/api/quizzes/{quiz.id}/results/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["score_percentage"] == 100
        assert data["questions"][0]["is_correct"] is True

    def test_results_not_found(self, api_client):
        resp = api_client.get("/api/quizzes/999/results/")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "QUIZ_NOT_FOUND"
