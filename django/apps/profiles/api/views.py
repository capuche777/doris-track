"""API views for the profiles app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.selectors import get_student_by_email
from core.exceptions import StudentNotFound

from .serializers import StudentSerializer


class StudentByEmailView(APIView):
    """Resolve a student by email at the start of a Doris session."""

    @extend_schema(
        summary="Look up a student by email",
        description="Returns the student profile matching the given email.",
        parameters=[
            OpenApiParameter(
                name="email",
                type=OpenApiTypes.EMAIL,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Email address of the student to look up.",
            )
        ],
        responses={
            200: StudentSerializer,
            400: OpenApiResponse(description="Missing email query parameter"),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Students"],
    )
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            raise ValidationError({"email": "This query parameter is required."})

        student = get_student_by_email(email)
        if student is None:
            raise StudentNotFound()

        return Response(StudentSerializer(student).data)
