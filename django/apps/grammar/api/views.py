"""API views for the grammar app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.grammar.models import Correction
from apps.grammar.selectors import get_corrections
from apps.grammar.services import get_common_mistakes, get_mistake_trend, log_correction
from apps.profiles.selectors import get_student_profile
from core.exceptions import StudentNotFound
from core.query_params import parse_iso_date, parse_positive_int

from .serializers import (
    CorrectionCreateSerializer,
    CorrectionSerializer,
    MistakeCategorySerializer,
    MistakeTrendPointSerializer,
)

DEFAULT_CORRECTIONS_LIMIT = 50
DEFAULT_ANALYTICS_PERIOD_DAYS = 30
DEFAULT_TREND_WEEKS = 8
CATEGORY_VALUES = {value for value, _ in Correction.CATEGORY_CHOICES}


def _get_student_or_404(student_id):
    student = get_student_profile(student_id)
    if student is None:
        raise StudentNotFound()
    return student


class CorrectionListCreateView(APIView):
    """List a student's grammar corrections or log a new one."""

    @extend_schema(
        summary="List grammar corrections",
        description="Returns corrections for a student, newest first, with filters.",
        parameters=[
            OpenApiParameter("category", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter by category."),
            OpenApiParameter("date_from", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Inclusive start date (YYYY-MM-DD)."),
            OpenApiParameter("date_to", OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description="Inclusive end date (YYYY-MM-DD)."),
            OpenApiParameter("limit", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description=f"Max results (default {DEFAULT_CORRECTIONS_LIMIT})."),
        ],
        responses={200: CorrectionSerializer(many=True),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Grammar"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        limit = parse_positive_int(request, "limit", DEFAULT_CORRECTIONS_LIMIT)
        corrections = get_corrections(
            student,
            category=request.query_params.get("category"),
            date_from=parse_iso_date(request, "date_from"),
            date_to=parse_iso_date(request, "date_to"),
        )[:limit]
        return Response(
            {"corrections": CorrectionSerializer(corrections, many=True).data}
        )

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
        student = _get_student_or_404(student_id)

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


class CorrectionAnalyticsView(APIView):
    """Common grammar mistake categories over a period."""

    @extend_schema(
        summary="Grammar mistake analytics",
        description="Mistake categories ranked by frequency over the lookback period.",
        parameters=[
            OpenApiParameter("period_days", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description=f"Lookback days (default {DEFAULT_ANALYTICS_PERIOD_DAYS})."),
        ],
        responses={200: MistakeCategorySerializer(many=True),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Grammar"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        period_days = parse_positive_int(
            request, "period_days", DEFAULT_ANALYTICS_PERIOD_DAYS
        )
        categories = get_common_mistakes(student, period_days=period_days)
        return Response({"period_days": period_days, "categories": categories})


class CorrectionTrendView(APIView):
    """Weekly trend for a single grammar category."""

    @extend_schema(
        summary="Grammar mistake trend",
        description="Per-week mistake counts for one category.",
        parameters=[
            OpenApiParameter("weeks", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description=f"Weeks to show (default {DEFAULT_TREND_WEEKS})."),
        ],
        responses={200: MistakeTrendPointSerializer(many=True),
                   400: OpenApiResponse(description="Invalid category"),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Grammar"],
    )
    def get(self, request, student_id, category):
        student = _get_student_or_404(student_id)
        if category not in CATEGORY_VALUES:
            raise ValidationError(
                {"category": f"Must be one of: {', '.join(sorted(CATEGORY_VALUES))}."}
            )
        weeks = parse_positive_int(request, "weeks", DEFAULT_TREND_WEEKS)
        trend = get_mistake_trend(student, category, weeks=weeks)
        return Response({"category": category, "trend": trend})
