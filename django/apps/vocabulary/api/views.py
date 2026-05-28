"""API views for the vocabulary app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.selectors import get_student_profile
from apps.vocabulary.models import Word
from apps.vocabulary.selectors import (
    get_difficult_words_detailed,
    get_due_words_count,
    get_words_by_mastery,
    get_words_for_review,
)
from apps.vocabulary.services import (
    check_review_answer,
    create_word,
    update_word,
    word_exists,
)
from core.exceptions import StudentNotFound, WordAlreadyExists, WordNotFound
from core.query_params import parse_positive_int

from .serializers import (
    DifficultWordSerializer,
    ReviewAnswerSerializer,
    ReviewResultSerializer,
    WordCreateSerializer,
    WordSerializer,
    WordUpdateSerializer,
)

DEFAULT_DUE_LIMIT = 20
DEFAULT_DIFFICULT_LIMIT = 10
DEFAULT_DIFFICULT_THRESHOLD = 3
MASTERY_VALUES = {value for value, _ in Word.MASTERY_CHOICES}


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

        limit = parse_positive_int(request, "limit", DEFAULT_DUE_LIMIT)
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


class AddWordView(APIView):
    """Add a new vocabulary word for a student."""

    @extend_schema(
        summary="Add a vocabulary word",
        description="Creates a new word for the student. Rejects duplicates.",
        request=WordCreateSerializer,
        responses={
            201: WordSerializer,
            400: OpenApiResponse(description="Validation error or duplicate word"),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Vocabulary"],
    )
    def post(self, request, student_id):
        student = get_student_profile(student_id)
        if student is None:
            raise StudentNotFound()

        serializer = WordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if word_exists(student, data["word"]):
            raise WordAlreadyExists()

        word = create_word(
            student,
            word=data["word"],
            definition=data["definition"],
            difficulty=data["difficulty"],
            example_sentence=data["example_sentence"],
            collocations=", ".join(data["collocations"]),
            accepted_answers=data["accepted_answers"],
        )
        return Response(WordSerializer(word).data, status=status.HTTP_201_CREATED)


class WordUpdateView(APIView):
    """Update a vocabulary word's editable content (e.g. accepted answers)."""

    @extend_schema(
        summary="Update a vocabulary word",
        description=(
            "Partially updates a word's editable content fields (word, "
            "definition, difficulty, example_sentence, collocations, "
            "accepted_answers). Spaced-repetition state is left untouched."
        ),
        request=WordUpdateSerializer,
        responses={
            200: WordSerializer,
            400: OpenApiResponse(description="Validation error or duplicate word"),
            404: OpenApiResponse(description="Word not found"),
        },
        tags=["Vocabulary"],
    )
    def patch(self, request, word_id):
        word = Word.objects.filter(id=word_id).first()
        if word is None:
            raise WordNotFound()

        serializer = WordUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        new_word = data.get("word")
        if (
            new_word is not None
            and new_word != word.word
            and Word.objects.filter(student=word.student, word=new_word)
            .exclude(id=word.id)
            .exists()
        ):
            raise WordAlreadyExists()

        # collocations are stored as comma-separated text, exposed as a list.
        if "collocations" in data:
            data["collocations"] = ", ".join(data["collocations"])

        updated = update_word(word_id, **data)
        return Response(WordSerializer(updated).data)


class DifficultWordsView(APIView):
    """List the words a student keeps getting wrong."""

    @extend_schema(
        summary="List difficult words",
        description="Words with `times_wrong >= threshold`, hardest first.",
        parameters=[
            OpenApiParameter(
                name="limit", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                required=False,
                description=f"Max words to return (default {DEFAULT_DIFFICULT_LIMIT}).",
            ),
            OpenApiParameter(
                name="threshold", type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY, required=False,
                description=(
                    "Minimum times_wrong to qualify "
                    f"(default {DEFAULT_DIFFICULT_THRESHOLD})."
                ),
            ),
        ],
        responses={
            200: DifficultWordSerializer(many=True),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Vocabulary"],
    )
    def get(self, request, student_id):
        student = get_student_profile(student_id)
        if student is None:
            raise StudentNotFound()

        limit = parse_positive_int(request, "limit", DEFAULT_DIFFICULT_LIMIT)
        threshold = parse_positive_int(request, "threshold", DEFAULT_DIFFICULT_THRESHOLD)
        result = get_difficult_words_detailed(student, limit=limit, threshold=threshold)

        words = [
            {
                "id": item["word"].id,
                "word": item["word"].word,
                "times_wrong": item["times_wrong"],
                "review_count": item["review_count"],
                "failure_rate": item["failure_rate"],
            }
            for item in result
        ]
        return Response({"words": words})


class WordsByMasteryView(APIView):
    """List a student's words filtered by mastery level."""

    @extend_schema(
        summary="List words by mastery",
        description="Words in the given mastery state (new, learning, mastered).",
        responses={
            200: WordSerializer(many=True),
            400: OpenApiResponse(description="Invalid mastery value"),
            404: OpenApiResponse(description="Student not found"),
        },
        tags=["Vocabulary"],
    )
    def get(self, request, student_id, mastery):
        student = get_student_profile(student_id)
        if student is None:
            raise StudentNotFound()

        if mastery not in MASTERY_VALUES:
            raise ValidationError(
                {"mastery": f"Must be one of: {', '.join(sorted(MASTERY_VALUES))}."}
            )

        words = get_words_by_mastery(student, mastery)
        return Response({"words": WordSerializer(words, many=True).data})
