"""API views for the practice app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.practice.selectors import get_sessions
from apps.practice.services import (
    get_practice_breakdown,
    get_practice_streak,
    log_practice,
)
from apps.profiles.selectors import get_student_profile
from core.exceptions import StudentNotFound
from core.query_params import parse_iso_date, parse_positive_int

from .serializers import (
    PracticeCreateSerializer,
    PracticeSessionSerializer,
    PracticeStatsSerializer,
    PracticeStreakSerializer,
)

DEFAULT_SESSIONS_LIMIT = 20
DEFAULT_STATS_DAYS = 30


def _get_student_or_404(student_id):
    student = get_student_profile(student_id)
    if student is None:
        raise StudentNotFound()
    return student


class PracticeListCreateView(APIView):
    """List a student's practice sessions or log a new one."""

    @extend_schema(
        summary="List practice sessions",
        description="Returns practice sessions for a student, newest first.",
        parameters=[
            OpenApiParameter("practice_type", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by practice type."),
            OpenApiParameter("date_from", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Inclusive start date (YYYY-MM-DD)."),
            OpenApiParameter("date_to", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Inclusive end date (YYYY-MM-DD)."),
            OpenApiParameter("limit", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description=f"Max results (default {DEFAULT_SESSIONS_LIMIT})."),
        ],
        responses={200: PracticeSessionSerializer(many=True),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Practice"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        limit = parse_positive_int(request, "limit", DEFAULT_SESSIONS_LIMIT)
        sessions = get_sessions(
            student,
            date_from=parse_iso_date(request, "date_from"),
            date_to=parse_iso_date(request, "date_to"),
            practice_type=request.query_params.get("practice_type"),
        )[:limit]
        return Response(
            {"sessions": PracticeSessionSerializer(sessions, many=True).data}
        )

    @extend_schema(
        summary="Log a practice session",
        request=PracticeCreateSerializer,
        responses={
            201: PracticeSessionSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Practice"],
    )
    def post(self, request, student_id):
        student = _get_student_or_404(student_id)

        serializer = PracticeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session = log_practice(
            student,
            practice_type=data["practice_type"],
            duration_minutes=data["duration_minutes"],
            notes=data.get("notes", ""),
            date_obj=data.get("date"),
        )
        return Response(
            PracticeSessionSerializer(session).data, status=status.HTTP_201_CREATED
        )


class PracticeStreakView(APIView):
    """Current consecutive-day practice streak."""

    @extend_schema(
        summary="Get practice streak",
        responses={200: PracticeStreakSerializer,
                   404: OpenApiResponse(description="Student not found")},
        tags=["Practice"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        return Response({"streak": get_practice_streak(student)})


class PracticeStatsView(APIView):
    """Aggregate practice statistics with per-type breakdown."""

    @extend_schema(
        summary="Get practice stats",
        description="Totals plus per-type session and minute counts over N days.",
        parameters=[
            OpenApiParameter("days", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description=f"Lookback days (default {DEFAULT_STATS_DAYS})."),
        ],
        responses={200: PracticeStatsSerializer,
                   404: OpenApiResponse(description="Student not found")},
        tags=["Practice"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        days = parse_positive_int(request, "days", DEFAULT_STATS_DAYS)
        return Response(get_practice_breakdown(student, days=days))
