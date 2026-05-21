"""Tests for practice app."""
import pytest
from datetime import date
from apps.profiles.models import Student
from apps.practice.models import PracticeSession
from apps.practice.services import create_session


@pytest.mark.django_db
class TestPracticeSession:
    def test_session_creation(self):
        student = Student.objects.create(name="John", email="john@test.com")
        session = create_session(student, "vocabulary", 30, "Reviewed 10 words")
        assert session.practice_type == "vocabulary"
        assert session.duration_minutes == 30
