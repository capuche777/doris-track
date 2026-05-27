"""API views for the dashboard app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.selectors import get_dashboard_for_api
from apps.profiles.selectors import get_student_profile
from core.exceptions import StudentNotFound


class DashboardView(APIView):
    """One call returning a full progress snapshot for a student."""

    @extend_schema(
        summary="Get student dashboard",
        description=(
            "Aggregates scores, vocabulary, practice, grammar and quiz data "
            "for a student. Used by Doris for progress reports."
        ),
        responses={
            200: OpenApiResponse(OpenApiTypes.OBJECT, description="Dashboard snapshot"),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Dashboard"],
    )
    def get(self, request, student_id):
        student = get_student_profile(student_id)
        if student is None:
            raise StudentNotFound()
        return Response(get_dashboard_for_api(student))
