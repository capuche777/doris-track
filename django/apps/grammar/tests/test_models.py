"""Tests for grammar app."""
import pytest
from datetime import date
from apps.profiles.models import Student
from apps.grammar.models import Correction
from apps.grammar.services import log_correction


@pytest.mark.django_db
class TestCorrectionModel:
    def test_correction_creation(self):
        student = Student.objects.create(name="John", email="john@test.com")
        corr = Correction.objects.create(
            student=student,
            date=date.today(),
            student_mistake="I go yesterday",
            correct_version="I went yesterday",
            grammar_rule="Past simple of go",
            category="verb_tenses",
        )
        assert corr.category == "verb_tenses"

    def test_log_correction_service(self):
        student = Student.objects.create(name="John", email="john2@test.com")
        corr = log_correction(student, "mistake", "correct", category="prepositions")
        assert corr.category == "prepositions"
