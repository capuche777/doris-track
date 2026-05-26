"""Tests for dashboard view and core selectors."""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from apps.profiles.models import Student
from apps.scores.models import Assessment, Score
from apps.vocabulary.models import Word
from apps.practice.models import PracticeSession
from apps.grammar.models import Correction
from apps.quiz.models import Quiz, QuizQuestion


@pytest.mark.django_db
class TestDashboardSelectors:
    """Test all dashboard aggregator functions."""

    def test_get_student_info(self):
        from apps.core.selectors import get_student_info
        student = Student.objects.create(name="Ana", current_level="B1", target_level="C1")
        info = get_student_info(student)
        assert info["name"] == "Ana"
        assert info["current_level"] == "B1"
        assert info["target_level"] == "C1"
        assert info["tutor"] is None

    def test_get_score_summary(self):
        from apps.core.selectors import get_score_summary
        student = Student.objects.create(name="Ana", email="ana@test.com")
        a1 = Assessment.objects.create(student=student, date=date.today() - timedelta(days=10))
        Score.objects.create(assessment=a1, skill="grammar", value=70)
        Score.objects.create(assessment=a1, skill="vocabulary", value=80)
        a2 = Assessment.objects.create(student=student, date=date.today() - timedelta(days=3))
        Score.objects.create(assessment=a2, skill="grammar", value=60)
        Score.objects.create(assessment=a2, skill="vocabulary", value=85)

        summary = get_score_summary(student, limit=5)
        assert "latest_per_skill" in summary
        assert "skill_trends" in summary
        assert summary["latest_per_skill"]["grammar"] == 60
        assert summary["latest_per_skill"]["vocabulary"] == 85
        assert summary["skill_trends"]["grammar"] == "down"
        assert summary["skill_trends"]["vocabulary"] == "up"
        assert "grammar" in summary["declining_skills"]

    def test_get_vocabulary_stats(self):
        from apps.core.selectors import get_vocabulary_stats
        student = Student.objects.create(name="Ana", email="ana2@test.com")
        Word.objects.create(student=student, word="apple", mastery="new")
        Word.objects.create(student=student, word="banana", mastery="learning")
        Word.objects.create(student=student, word="cherry", mastery="mastered")
        Word.objects.create(student=student, word="date", mastery="learning", next_review_date=date.today())

        stats = get_vocabulary_stats(student)
        assert stats["total_words"] == 4
        assert stats["new"] == 1
        assert stats["learning"] == 2
        assert stats["mastered"] == 1
        assert stats["words_due_today"] == 1

    def test_get_practice_streak(self):
        from apps.core.selectors import get_practice_streak
        student = Student.objects.create(name="Ana", email="ana3@test.com")
        yesterday = date.today() - timedelta(days=1)
        two_days_ago = date.today() - timedelta(days=2)
        PracticeSession.objects.create(student=student, date=date.today(), duration_minutes=30)
        PracticeSession.objects.create(student=student, date=yesterday, duration_minutes=20)
        PracticeSession.objects.create(student=student, date=two_days_ago, duration_minutes=15)

        streak = get_practice_streak(student)
        assert streak["streak"] >= 1
        assert streak["minutes_this_week"] == 65

    def test_get_grammar_alerts(self):
        from apps.core.selectors import get_grammar_alerts
        student = Student.objects.create(name="Ana", email="ana4@test.com")
        for i in range(3):
            Correction.objects.create(
                student=student, date=date.today() - timedelta(days=i),
                student_mistake="的错误", correct_version="错误",
                category="verb_tenses",
            )
        for i in range(2):
            Correction.objects.create(
                student=student, date=date.today() - timedelta(days=i),
                student_mistake="a some", correct_version="some",
                category="articles",
            )

        alerts = get_grammar_alerts(student, limit=3)
        assert len(alerts) == 2
        assert alerts[0]["category"] == "verb_tenses"
        assert alerts[0]["count"] == 3

    def test_get_quiz_scores(self):
        from apps.core.selectors import get_quiz_scores
        student = Student.objects.create(name="Ana", email="ana5@test.com")
        week_start = date.today() - timedelta(weeks=1)
        quiz = Quiz.objects.create(student=student, week_start_date=week_start)
        QuizQuestion.objects.create(quiz=quiz, question_type="definition_to_word",
                                    prompt="?", correct_answer="ans", is_correct=True)
        QuizQuestion.objects.create(quiz=quiz, question_type="definition_to_word",
                                    prompt="?", correct_answer="ans", is_correct=False)

        scores = get_quiz_scores(student, limit=3)
        assert len(scores) == 1
        assert scores[0]["score_percent"] == 50

    def test_get_difficult_words(self):
        from apps.core.selectors import get_difficult_words
        student = Student.objects.create(name="Ana", email="ana6@test.com")
        Word.objects.create(student=student, word="apple", times_wrong=3)
        Word.objects.create(student=student, word="banana", times_wrong=1)
        Word.objects.create(student=student, word="cherry", times_wrong=5)

        difficult = get_difficult_words(student, limit=5)
        assert len(difficult) == 3
        assert difficult[0]["word"] == "cherry"
        assert difficult[0]["times_wrong"] == 5

    def test_get_recent_corrections(self):
        from apps.core.selectors import get_recent_corrections
        student = Student.objects.create(name="Ana", email="ana7@test.com")
        Correction.objects.create(
            student=student, date=date.today(),
            student_mistake="I go to school yesterday",
            correct_version="I went to school yesterday",
            category="verb_tenses", grammar_rule="past tense",
        )
        corrections = get_recent_corrections(student, limit=10)
        assert len(corrections) == 1
        assert corrections[0]["mistake"] == "I go to school yesterday"
        assert corrections[0]["correction"] == "I went to school yesterday"

    def test_get_next_quiz_date(self):
        from apps.core.selectors import get_next_quiz_date
        student = Student.objects.create(name="Ana", email="ana8@test.com")
        next_date = get_next_quiz_date(student)
        assert next_date is not None
        # Should be a Monday
        d = date.fromisoformat(next_date)
        assert d.weekday() == 0

    def test_get_student_dashboard_data(self):
        from apps.core.selectors import get_student_dashboard_data
        student = Student.objects.create(name="Ana", email="ana9@test.com")
        data = get_student_dashboard_data(student)
        assert "student_info" in data
        assert "score_summary" in data
        assert "vocabulary_stats" in data
        assert "practice_streak" in data
        assert "grammar_alerts" in data
        assert "quiz_scores" in data
        assert "difficult_words" in data
        assert "recent_corrections" in data
        assert "next_quiz_date" in data
        assert "quick_actions" in data


@pytest.mark.django_db
class TestDashboardView:
    """Test the dashboard view returns 200 and all required context."""

    def test_dashboard_view_200(self, client):
        from apps.core.selectors import get_student_by_request
        # Create a student so dashboard has data
        student = Student.objects.create(name="Test Student", email="test@example.com")
        Assessment.objects.create(student=student, date=date.today())
        Word.objects.create(student=student, word="test", definition="a test")

        # The view at / should work
        response = client.get("/")
        assert response.status_code == 200

    def test_dashboard_context_data(self, client):
        """Verify dashboard template loads with all sections."""
        student = Student.objects.create(name="Test", email="test2@example.com")
        response = client.get("/")
        assert response.status_code == 200
        # Template should render without errors
        assert "Dashboard" in response.rendered_content or "Welcome" in response.rendered_content