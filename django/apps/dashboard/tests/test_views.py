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

    def test_dashboard_renders_for_existing_student(self, client, django_user_model):
        """Should return 200 and render the dashboard template when a student exists."""
        user = django_user_model.objects.create_user(
            username="tutor", password="pw", email="doris@test.com"
        )
        client.force_login(user)
        Student.objects.create(name="Doris", email="doris@test.com")

        response = client.get(reverse("dashboard:home"))

        assert response.status_code == 200
        assert "dashboard/dashboard.html" in [t.name for t in response.templates]
        assert response.context["student"] is not None
        assert response.context["dashboard"] is not None

    def test_dashboard_redirects_anonymous_to_login(self, client):
        """Unauthenticated visitors are redirected to the login page site-wide."""
        response = client.get(reverse("dashboard:home"))

        assert response.status_code == 302
        assert response.url == "/login/?next=/"

    def test_static_assets_are_exempt_from_login(self, client):
        """Static files must stay reachable so the login page keeps its CSS."""
        response = client.get("/static/css/main.css")

        assert response.status_code != 302
