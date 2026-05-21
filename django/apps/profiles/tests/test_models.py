"""Tests for profiles app models."""
import pytest
from apps.profiles.models import Student, Tutor


@pytest.mark.django_db
class TestStudentModel:
    def test_student_creation(self):
        tutor = Tutor.objects.create(name="Jane Doe", email="jane@example.com")
        student = Student.objects.create(
            name="John Doe",
            email="john@example.com",
            current_level="B1",
            target_level="C1",
            tutor=tutor,
        )
        assert student.name == "John Doe"
        assert student.current_level == "B1"
        assert student.target_level == "C1"
        assert student.tutor == tutor

    def test_student_str(self):
        student = Student.objects.create(name="John", email="john@test.com")
        assert str(student) == "John (B1 → C1)"
