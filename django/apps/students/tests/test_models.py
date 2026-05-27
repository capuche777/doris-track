"""Unit tests for the students app Student model."""
import pytest
from django.contrib.auth.models import User

from apps.students.models import Student

pytestmark = pytest.mark.django_db


class TestStudentModel:
    """Tests for the legacy Student model linking a Django User."""

    def test_str_returns_username(self):
        """__str__ should return the linked user's username."""
        user = User.objects.create_user(username="doris", password="secret")
        student = Student.objects.create(user=user)
        assert str(student) == "doris"

    def test_one_to_one_user_relation(self):
        """The user should be reachable via the student_profile reverse accessor."""
        user = User.objects.create_user(username="doris2", password="secret")
        student = Student.objects.create(user=user)
        assert user.student_profile == student

    def test_created_at_is_set_automatically(self):
        """created_at should be populated on save."""
        user = User.objects.create_user(username="doris3", password="secret")
        student = Student.objects.create(user=user)
        assert student.created_at is not None
