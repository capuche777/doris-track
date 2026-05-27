"""API views for the grammar app."""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.grammar.services import log_correction
from apps.profiles.selectors import get_student_profile
from core.exceptions import StudentNotFound

from .serializers import CorrectionCreateSerializer, CorrectionSerializer


class CorrectionCreateView(APIView):
    """Log a grammar correction for a student."""

    @extend_schema(
        summary="Log a grammar correction",
        description="Records a mistake and its correction; the date is set to today.",
        request=CorrectionCreateSerializer,
        responses={
            201: CorrectionSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Grammar"],
    )
    def post(self, request, student_id):
        student = get_student_profile(student_id)
        if student is None:
            raise StudentNotFound()

        serializer = CorrectionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        correction = log_correction(
            student,
            mistake=data["student_mistake"],
            correct=data["correct_version"],
            rule=data.get("grammar_rule", ""),
            category=data.get("category", "other"),
        )

        return Response(
            CorrectionSerializer(correction).data, status=status.HTTP_201_CREATED
        )
