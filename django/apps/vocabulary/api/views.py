"""API views for the vocabulary app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.selectors import get_student_profile
from apps.vocabulary.models import Word
from apps.vocabulary.selectors import get_due_words_count, get_words_for_review
from apps.vocabulary.services import check_review_answer
from core.exceptions import StudentNotFound, WordNotFound

from .serializers import ReviewAnswerSerializer, ReviewResultSerializer, WordSerializer

DEFAULT_DUE_LIMIT = 20


def _parse_limit(request, default):
    """Parse a positive ``limit`` query param, falling back to ``default``."""
    raw = request.query_params.get("limit")
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


class WordsDueView(APIView):
    """List the words due for review for a student."""

    @extend_schema(
        summary="List words due for review",
        description=(
            "Returns vocabulary words due for review today or earlier "
            "(excluding mastered words). `count` is the total number due; "
            "`words` is capped by `limit`."
        ),
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description=f"Max words to return (default {DEFAULT_DUE_LIMIT}).",
            )
        ],
        responses={
            200: WordSerializer(many=True),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Vocabulary"],
    )
    def get(self, request, student_id):
        student = get_student_profile(student_id)
        if student is None:
            raise StudentNotFound()

        limit = _parse_limit(request, DEFAULT_DUE_LIMIT)
        words = get_words_for_review(student)[:limit]

        return Response(
            {
                "count": get_due_words_count(student),
                "words": WordSerializer(words, many=True).data,
            }
        )


class WordReviewView(APIView):
    """Submit and grade a vocabulary review answer."""

    @extend_schema(
        summary="Submit a review answer",
        description=(
            "Grades the student's answer against the word, updates its "
            "spaced-repetition state, and returns the result."
        ),
        request=ReviewAnswerSerializer,
        responses={
            200: ReviewResultSerializer,
            400: OpenApiResponse(description="student_answer is required"),
            404: OpenApiResponse(description="Word not found"),
        },
        tags=["Vocabulary"],
    )
    def post(self, request, word_id):
        if not Word.objects.filter(id=word_id).exists():
            raise WordNotFound()

        serializer = ReviewAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = check_review_answer(word_id, serializer.validated_data["student_answer"])
        word = Word.objects.get(id=word_id)

        return Response(
            {
                "correct": result["correct"],
                "correct_answer": result["correct_answer"],
                "next_review": result["next_review"],
                "mastery": word.mastery,
                "current_interval_days": word.current_interval_days,
            }
        )
