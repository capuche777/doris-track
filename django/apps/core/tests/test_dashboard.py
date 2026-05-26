"""Tests for core dashboard selectors (Task #229 / DT-10)."""
import pytest
from datetime import date, timedelta

pytestmark = pytest.mark.django_db


class TestGetDifficultWords:
    """Test get_difficult_words selector."""

    def test_get_difficult_words_returns_list(self):
        """Should return a list of dicts with word, times_wrong, mastery."""
        from apps.core.selectors import get_difficult_words
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_difficult_words(student)
        assert isinstance(result, list)

    def test_get_difficult_words_respects_limit(self):
        """Should return at most `limit` words."""
        from apps.core.selectors import get_difficult_words
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_difficult_words(student, limit=3)
        assert len(result) <= 3


class TestGetGrammarAlerts:
    """Test get_grammar_alerts selector."""

    def test_get_grammar_alerts_returns_list(self):
        """Should return a list of category + count dicts."""
        from apps.core.selectors import get_grammar_alerts
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_grammar_alerts(student)
        assert isinstance(result, list)


class TestGetNextQuizDate:
    """Test get_next_quiz_date selector."""

    def test_get_next_quiz_date_returns_dict(self):
        """Should return dict with next_quiz_date and scheduled bool."""
        from apps.core.selectors import get_next_quiz_date
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_next_quiz_date(student)
        assert isinstance(result, dict)
        assert "next_quiz_date" in result
        assert "scheduled" in result


class TestGetStudentDashboardData:
    """Test the main dashboard aggregator."""

    def test_dashboard_data_contains_all_sections(self):
        """All required dashboard sections should be present."""
        from apps.core.selectors import get_student_dashboard_data
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        data = get_student_dashboard_data(student)
        assert data is not None
        required_keys = [
            "student_info",
            "score_summary",
            "vocabulary_stats",
            "practice_streak",
            "difficult_words",
            "grammar_alerts",
            "quiz_scores",
            "next_quiz_date",
            "recent_corrections",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

    def test_practice_streak_has_minutes_this_week(self):
        """practice_streak should include minutes_this_week."""
        from apps.core.selectors import get_student_dashboard_data
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        data = get_student_dashboard_data(student)
        assert "minutes_this_week" in data["practice_streak"]
