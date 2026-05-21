"""Tests for quiz app."""
import pytest
from datetime import date, timedelta
from apps.profiles.models import Student
from apps.vocabulary.models import Word
from apps.quiz.models import Quiz, QuizQuestion
from apps.quiz.services import generate_weekly_quiz


@pytest.mark.django_db
class TestQuizModels:
    def test_quiz_creation(self):
        student = Student.objects.create(name="John", email="john@test.com")
        week_start = date.today() - timedelta(days=date.today().weekday())
        quiz = Quiz.objects.create(student=student, week_start_date=week_start)
        assert quiz.student == student

    def test_generate_weekly_quiz(self):
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="test",
            definition="a procedure for testing",
            next_review_date=date.today(),
        )
        quiz = generate_weekly_quiz(student)
        assert quiz.student == student
        assert quiz.questions.count() >= 1
