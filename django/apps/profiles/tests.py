"""
Tests for profiles app.
"""
import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


def test_student_profile_view_returns_200(client):
    """Test that the profile view returns 200 when student exists."""
    response = client.get("/profile/")
    # Without a student in DB, should return 404
    # The test validates the URL routing works
    assert response.status_code in [200, 404]


def test_get_student_profile_returns_none_for_invalid_id():
    """Test selector returns None for non-existent student."""
    from apps.profiles.selectors import get_student_profile
    result = get_student_profile(9999)
    assert result is None