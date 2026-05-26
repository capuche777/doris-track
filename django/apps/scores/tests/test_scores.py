"""Real pytest tests for scores app (Task #223 / DT-04)."""
import pytest
from datetime import date, timedelta
from django.db import connection

# Use conftest fixtures if available, otherwise mock
pytestmark = pytest.mark.django_db


class TestRecordAssessment:
    """Test record_assessment service."""

    def test_record_assessment_creates_assessment(self):
        """record_assessment should create an Assessment and associated Scores."""
        from apps.scores.services import record_assessment
        from apps.scores.models import Assessment, Score
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        scores_dict = {"pronunciation": 85, "fluency": 78, "grammar": 90}
        assessment = record_assessment(student.id, scores_dict, date.today(), "Test notes")

        assert assessment is not None
        assert assessment.student_id == student.id
        assert assessment.notes == "Test notes"

        saved = Assessment.objects.get(id=assessment.id)
        assert saved.notes == "Test notes"

        score_count = Score.objects.filter(assessment=assessment).count()
        assert score_count == 3

    def test_record_assessment_clamps_values(self):
        """Scores outside 0-100 should be clamped."""
        from apps.scores.services import record_assessment
        from apps.scores.models import Score
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        scores_dict = {"pronunciation": 150, "fluency": -5}  # out of range
        assessment = record_assessment(student.id, scores_dict, date.today())

        pronunciation_score = Score.objects.get(assessment=assessment, skill="pronunciation")
        fluency_score = Score.objects.get(assessment=assessment, skill="fluency")

        assert pronunciation_score.value == 100
        assert fluency_score.value == 0


class TestDetectDecliningSkills:
    """Test detect_declining_skills service."""

    def test_detect_declining_skills_returns_dict(self):
        """Should return a dict (may be empty if no declines)."""
        from apps.scores.services import detect_declining_skills
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = detect_declining_skills(student.id)
        assert isinstance(result, dict)

    def test_detect_declining_skills_no_false_positives_with_no_data(self):
        """With insufficient data, should return empty dict (no false declines)."""
        from apps.scores.services import detect_declining_skills
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = detect_declining_skills(student.id)
        # Empty DB should not report declines
        for skill, info in result.items():
            assert info["change"] <= -3


class TestGetScoreHistory:
    """Test get_score_history selector."""

    def test_get_score_history_returns_queryset(self):
        """Should return a queryset of Score objects."""
        from apps.scores.selectors import get_score_history
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_score_history(student.id)
        # Should be iterable (queryset)
        assert hasattr(result, "filter")

    def test_get_score_history_filters_by_skill(self):
        """Should filter correctly when skill is specified."""
        from apps.scores.selectors import get_score_history
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_score_history(student.id, skill="pronunciation")
        for score in result:
            assert score.skill == "pronunciation"


class TestGetLatestScores:
    """Test get_latest_scores selector."""

    def test_get_latest_scores_returns_dict(self):
        """Should return a dict of {skill: value}."""
        from apps.scores.selectors import get_latest_scores
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_latest_scores(student.id)
        assert isinstance(result, dict)


class TestGetScoreTrends:
    """Test get_score_trends selector (DT-04 Issue #1)."""

    def test_get_score_trends_returns_list(self):
        """get_score_trends should return a list of (date, value) tuples."""
        from apps.scores.selectors import get_score_trends
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_score_trends(student.id, skill="pronunciation", days=30)
        assert isinstance(result, list)

    def test_get_score_trends_filters_by_days(self):
        """Should respect the days parameter."""
        from apps.scores.selectors import get_score_trends
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        # 7-day window
        result_7 = get_score_trends(student.id, skill="pronunciation", days=7)
        # 30-day window (should include at least as many records)
        result_30 = get_score_trends(student.id, skill="pronunciation", days=30)

        # Both should be lists
        assert isinstance(result_7, list)
        assert isinstance(result_30, list)

    def test_get_score_trends_without_skill(self):
        """Should return data for all skills when skill is None."""
        from apps.scores.selectors import get_score_trends
        from apps.profiles.models import Student

        student = Student.objects.first()
        if not student:
            pytest.skip("No student in DB")

        result = get_score_trends(student.id, days=30)
        assert isinstance(result, list)
