"""Integration tests for the dashboard view."""
import pytest
from django.urls import reverse

from apps.profiles.models import Student

pytestmark = pytest.mark.django_db


class TestDashboardView:
    """Tests for the main student dashboard view."""

    def test_dashboard_url_resolves_to_root(self):
        """The dashboard home URL should resolve to '/'."""
        assert reverse("dashboard:home") == "/"

    def test_dashboard_renders_for_existing_student(self, client):
        """Should return 200 and render the dashboard template when a student exists."""
        Student.objects.create(name="Doris", email="doris@test.com")

        response = client.get(reverse("dashboard:home"))

        assert response.status_code == 200
        assert "dashboard/dashboard.html" in [t.name for t in response.templates]
        assert response.context["student"] is not None
        assert response.context["dashboard"] is not None
