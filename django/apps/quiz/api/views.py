"""API views for the quiz app."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.selectors import get_student_profile
from apps.quiz.models import Quiz, QuizQuestion
from apps.quiz.selectors import get_quizzes
from apps.quiz.services import (
    generate_weekly_quiz,
    get_quiz_results_summary,
    submit_quiz_answer,
)
from core.exceptions import QuestionNotFound, QuizNotFound, StudentNotFound

from .serializers import (
    QuizAnswerSerializer,
    QuizQuestionResultSerializer,
    QuizQuestionSerializer,
)


def _get_student_or_404(student_id):
    student = get_student_profile(student_id)
    if student is None:
        raise StudentNotFound()
    return student


class QuizGenerateView(APIView):
    """Generate (or return) the current week's quiz for a student."""

    @extend_schema(
        summary="Generate a weekly quiz",
        description="Idempotent — returns the existing quiz if already generated.",
        request=None,
        responses={200: OpenApiResponse(OpenApiTypes.OBJECT, description="Quiz with questions"),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Quiz"],
    )
    def post(self, request, student_id):
        student = _get_student_or_404(student_id)
        quiz = generate_weekly_quiz(student)
        questions = quiz.questions.all()
        return Response(
            {
                "quiz_id": quiz.id,
                "week_start_date": quiz.week_start_date,
                "total_questions": questions.count(),
                "questions": QuizQuestionSerializer(questions, many=True).data,
            }
        )


class QuizAnswerView(APIView):
    """Submit and auto-grade an answer to a quiz question."""

    @extend_schema(
        summary="Answer a quiz question",
        request=QuizAnswerSerializer,
        responses={200: OpenApiResponse(OpenApiTypes.OBJECT, description="Grading result"),
                   400: OpenApiResponse(description="Validation error"),
                   404: OpenApiResponse(description="Question not found")},
        tags=["Quiz"],
    )
    def post(self, request, question_id):
        if not QuizQuestion.objects.filter(id=question_id).exists():
            raise QuestionNotFound()

        serializer = QuizAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_correct, feedback = submit_quiz_answer(
            question_id, serializer.validated_data["student_answer"]
        )
        return Response({"is_correct": is_correct, "feedback": feedback})


class QuizListView(APIView):
    """List a student's past quizzes with their results."""

    @extend_schema(
        summary="List quizzes with results",
        responses={200: OpenApiResponse(OpenApiTypes.OBJECT, description="Quiz summaries"),
                   404: OpenApiResponse(description="Student not found")},
        tags=["Quiz"],
    )
    def get(self, request, student_id):
        student = _get_student_or_404(student_id)
        quizzes = [get_quiz_results_summary(q) for q in get_quizzes(student)]
        return Response({"quizzes": quizzes})


class QuizResultsView(APIView):
    """Detailed results for a single quiz."""

    @extend_schema(
        summary="Get quiz results",
        responses={200: OpenApiResponse(OpenApiTypes.OBJECT, description="Detailed results"),
                   404: OpenApiResponse(description="Quiz not found")},
        tags=["Quiz"],
    )
    def get(self, request, quiz_id):
        quiz = Quiz.objects.filter(id=quiz_id).prefetch_related("questions").first()
        if quiz is None:
            raise QuizNotFound()

        summary = get_quiz_results_summary(quiz)
        summary["questions"] = QuizQuestionResultSerializer(
            quiz.questions.all(), many=True
        ).data
        return Response(summary)
