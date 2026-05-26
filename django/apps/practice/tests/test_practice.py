"""Tests for practice app — DT-08."""
import pytest
from datetime import date, timedelta
from django.test import TestCase

from apps.practice.models import PracticeSession
from apps.practice.services import get_practice_streak, get_practice_stats
from apps.practice.selectors import get_heatmap_data
from apps.profiles.models import Student


@pytest.fixture
def student(db):
    return Student.objects.create(name="Test Student", email="test@example.com")


class TestGetPracticeStreak:
    """Test streak calculation — DT-08."""

    def test_streak_zero_when_no_sessions(self, student):
        assert get_practice_streak(student) == 0

    def test_streak_one_for_single_today(self, student, db):
        PracticeSession.objects.create(
            student=student,
            practice_type="vocabulary",
            duration_minutes=30,
            date=date.today(),
        )
        assert get_practice_streak(student) == 1

    def test_streak_counts_consecutive_days(self, student, db):
        today = date.today()
        for i in range(5):
            PracticeSession.objects.create(
                student=student,
                practice_type="vocabulary",
                duration_minutes=20,
                date=today - timedelta(days=i),
            )
        assert get_practice_streak(student) == 5

    def test_streak_broken_by_gap(self, student, db):
        today = date.today()
        # Session today
        PracticeSession.objects.create(student=student, practice_type="vocabulary", duration_minutes=20, date=today)
        # Gap -2 days ago
        PracticeSession.objects.create(student=student, practice_type="vocabulary", duration_minutes=20, date=today - timedelta(days=3))
        # Streak should be 1 (today only)
        assert get_practice_streak(student) == 1

    def test_streak_starts_from_yesterday_if_no_today(self, student, db):
        yesterday = date.today() - timedelta(days=1)
        PracticeSession.objects.create(student=student, practice_type="vocabulary", duration_minutes=20, date=yesterday)
        assert get_practice_streak(student) == 1


class TestGetPracticeStats:
    """Test practice statistics — DT-08."""

    def test_stats_empty(self, student, db):
        stats = get_practice_stats(student, days=30)
        assert stats["total_minutes"] == 0
        assert stats["total_sessions"] == 0
        assert stats["avg_duration"] == 0

    def test_stats_aggregates_correctly(self, student, db):
        today = date.today()
        PracticeSession.objects.create(student=student, practice_type="vocabulary", duration_minutes=30, date=today)
        PracticeSession.objects.create(student=student, practice_type="writing", duration_minutes=45, date=today)
        stats = get_practice_stats(student, days=30)
        assert stats["total_minutes"] == 75
        assert stats["total_sessions"] == 2
        assert stats["avg_duration"] == 37.5
        assert stats["by_type"]["vocabulary"] == 30
        assert stats["by_type"]["writing"] == 45


class TestGetHeatmapData:
    """Test heatmap data generation — DT-08."""

    def test_heatmap_empty_year(self, student, db):
        data = get_heatmap_data(student, year=2020)
        assert data == {}

    def test_heatmap_aggregates_by_date(self, student, db):
        today = date.today()
        PracticeSession.objects.create(student=student, practice_type="vocabulary", duration_minutes=30, date=today)
        PracticeSession.objects.create(student=student, practice_type="vocabulary", duration_minutes=15, date=today)
        data = get_heatmap_data(student, year=today.year)
        assert data[today.isoformat()] == 45

    def test_heatmap_returns_dict(self, student, db):
        data = get_heatmap_data(student, year=date.today().year)
        assert isinstance(data, dict)
