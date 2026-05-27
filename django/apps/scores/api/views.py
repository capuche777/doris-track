"""API views for the scores app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.selectors import get_student_profile
from apps.scores.selectors import get_assessments, get_latest_scores
from apps.scores.services import detect_declining_skills, record_assessment
from core.exceptions import StudentNotFound
from core.query_params import parse_positive_int

from .serializers import (
    AssessmentCreateSerializer,
    AssessmentSerializer,
    ScoreHistoryItemSerializer,
    VALID_SKILLS,
)

DEFAULT_HISTORY_LIMIT = 20


def _get_student_or_404(student_id):
    student = get_student_profile(student_id)
    if student is None:
        raise StudentNotFound()
    return student


class AssessmentCreateView(APIView):
    """Record an assessment with skill scores for a student."""

    @extend_schema(
        summary="Record an assessment",
        request=AssessmentCreateSerializer,
        responses={
            201: AssessmentSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Scores"],
    )
    def post(self, request, student_id):
        student = _get_student_or_404(student_id)

        serializer = AssessmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        assessment = record_assessment(
            student.id,
            scores_dict=data["scores"],
            assessment_date=data["assessment_date"],
            notes=data.get("notes", ""),
        )
        return Response(
            AssessmentSerializer(assessment).data, status=status.HTTP_201_CREATED
        )


class ScoreHistoryView(APIView):
    """List a student's assessment scores, newest first."""

    @extend_schema(
        summary="Get score history",
        parameters=[
            OpenApiParameter("skill", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter scores to a single skill."),
            OpenApiParameter("limit", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description=f"Max assessments (default {DEFAULT_HISTORY_LIMIT})."),
        ],
        responses={200: ScoreHistoryItemSerializer(many=True),
                   400: OpenApiResponse(description="Invalid skill"),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Scores"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)

        skill = request.query_params.get("skill")
        if skill and skill not in VALID_SKILLS:
            raise ValidationError(
                {"skill": f"Must be one of: {', '.join(sorted(VALID_SKILLS))}."}
            )

        limit = parse_positive_int(request, "limit", DEFAULT_HISTORY_LIMIT)
        assessments = get_assessments(student.id, limit=limit)

        scores = []
        for assessment in assessments:
            values = {
                s.skill: s.value
                for s in assessment.scores.all()
                if not skill or s.skill == skill
            }
            scores.append(
                {"assessment_id": assessment.id, "date": assessment.date, "scores": values}
            )
        return Response({"scores": scores})


class LatestScoresView(APIView):
    """The most recent score per skill."""

    @extend_schema(
        summary="Get latest scores",
        responses={200: OpenApiResponse(OpenApiTypes.OBJECT, description="skill -> value"),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Scores"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        return Response(get_latest_scores(student.id))


class DecliningScoresView(APIView):
    """Skills that dropped >= 3 points over the last 7 days."""

    @extend_schema(
        summary="Get declining skills",
        responses={200: OpenApiResponse(OpenApiTypes.OBJECT, description="declining skills"),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Scores"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        return Response({"declining": detect_declining_skills(student.id)})
