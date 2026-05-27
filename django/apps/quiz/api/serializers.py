"""Serializers for the quiz API."""
from rest_framework import serializers

from apps.quiz.models import QuizQuestion


class QuizQuestionSerializer(serializers.ModelSerializer):
    """A generated quiz question (includes the answer key for the tutor bot)."""

    class Meta:
        model = QuizQuestion
        fields = ["id", "question_type", "prompt", "correct_answer"]


class QuizQuestionResultSerializer(serializers.ModelSerializer):
    """A quiz question with the student's answer and grading."""

    class Meta:
        model = QuizQuestion
        fields = [
            "id",
            "question_type",
            "prompt",
            "student_answer",
            "correct_answer",
            "is_correct",
        ]


class QuizAnswerSerializer(serializers.Serializer):
    """Input payload for answering a quiz question."""

    student_answer = serializers.CharField(allow_blank=True)
