"""Tests for quiz app."""
import pytest
from datetime import date, timedelta
from apps.profiles.models import Student
from apps.vocabulary.models import Word
from apps.quiz.models import Quiz, QuizQuestion
from apps.quiz.services import generate_weekly_quiz, submit_quiz_answer, get_quiz_results_summary


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

    def test_submit_quiz_answer_correct(self):
        student = Student.objects.create(name="John", email="john@test.com")
        week_start = date.today() - timedelta(days=date.today().weekday())
        quiz = Quiz.objects.create(student=student, week_start_date=week_start)
        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_type="definition_to_word",
            prompt="Definition: a procedure for testing",
            correct_answer="test",
        )
        is_correct, feedback = submit_quiz_answer(question.id, "test")
        assert is_correct is True
        assert "Correct" in feedback

    def test_submit_quiz_answer_incorrect(self):
        student = Student.objects.create(name="John", email="john@test.com")
        week_start = date.today() - timedelta(days=date.today().weekday())
        quiz = Quiz.objects.create(student=student, week_start_date=week_start)
        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_type="definition_to_word",
            prompt="Definition: a procedure for testing",
            correct_answer="test",
        )
        is_correct, feedback = submit_quiz_answer(question.id, "wrong")
        assert is_correct is False
        assert "Incorrect" in feedback

    def test_submit_quiz_answer_case_insensitive(self):
        student = Student.objects.create(name="John", email="john@test.com")
        week_start = date.today() - timedelta(days=date.today().weekday())
        quiz = Quiz.objects.create(student=student, week_start_date=week_start)
        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_type="definition_to_word",
            prompt="Definition: a procedure for testing",
            correct_answer="test",
        )
        is_correct, _ = submit_quiz_answer(question.id, "TEST")
        assert is_correct is True

    def test_quiz_results_summary(self):
        student = Student.objects.create(name="John", email="john@test.com")
        week_start = date.today() - timedelta(days=date.today().weekday())
        quiz = Quiz.objects.create(student=student, week_start_date=week_start)
        QuizQuestion.objects.create(
            quiz=quiz, question_type="definition_to_word",
            prompt="Q1", correct_answer="a", student_answer="a", is_correct=True
        )
        QuizQuestion.objects.create(
            quiz=quiz, question_type="definition_to_word",
            prompt="Q2", correct_answer="b", student_answer="wrong", is_correct=False
        )
        summary = get_quiz_results_summary(quiz)
        assert summary["total_questions"] == 2
        assert summary["correct_answers"] == 1
        assert summary["wrong_answers"] == 1
        assert summary["score_percentage"] == 50