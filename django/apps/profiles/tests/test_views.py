"""Tests for profiles app views and selectors."""
import pytest

from apps.profiles.models import Student
from apps.profiles.selectors import get_student_profile


@pytest.mark.django_db
def test_student_profile_view_returns_404_without_student(client):
    """The profile URL resolves and returns 404 when no student exists."""
    response = client.get("/profile/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_student_profile_view_returns_200_with_student(client):
    """The profile URL returns 200 when a student exists."""
    Student.objects.create(name="John", email="john@test.com")
    response = client.get("/profile/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_student_profile_returns_none_for_invalid_id():
    """Selector returns None for a non-existent student id."""
    assert get_student_profile(9999) is None


@pytest.mark.django_db
def test_get_student_profile_returns_student_for_valid_id():
    """Selector returns the matching student for an existing id."""
    student = Student.objects.create(name="Jane", email="jane@test.com")
    assert get_student_profile(student.id) == student
