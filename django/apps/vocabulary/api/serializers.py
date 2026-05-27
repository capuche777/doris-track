"""Serializers for the vocabulary API."""
from rest_framework import serializers

from apps.vocabulary.models import Word


class WordSerializer(serializers.ModelSerializer):
    """Vocabulary word with spaced-repetition state."""

    collocations = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = [
            "id",
            "word",
            "definition",
            "difficulty",
            "example_sentence",
            "collocations",
            "mastery",
            "review_count",
            "times_wrong",
            "next_review_date",
        ]

    def get_collocations(self, obj) -> list:
        """Expose the comma-separated text field as a list of strings."""
        return [c.strip() for c in obj.collocations.split(",") if c.strip()]


class ReviewAnswerSerializer(serializers.Serializer):
    """Input payload for submitting a vocabulary review answer."""

    student_answer = serializers.CharField(allow_blank=False)


class ReviewResultSerializer(serializers.Serializer):
    """Result of grading a vocabulary review answer."""

    correct = serializers.BooleanField()
    correct_answer = serializers.CharField()
    next_review = serializers.DateField(allow_null=True)
    mastery = serializers.CharField()
    current_interval_days = serializers.IntegerField()
