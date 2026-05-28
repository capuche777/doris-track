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
            "accepted_answers",
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


class WordCreateSerializer(serializers.Serializer):
    """Input payload for adding a new vocabulary word."""

    word = serializers.CharField(max_length=255)
    definition = serializers.CharField()
    difficulty = serializers.ChoiceField(
        choices=Word.DIFFICULTY_CHOICES, default="B2"
    )
    example_sentence = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    collocations = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    accepted_answers = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )


class WordUpdateSerializer(serializers.Serializer):
    """Input payload for partially updating a vocabulary word's content."""

    word = serializers.CharField(max_length=255, required=False)
    definition = serializers.CharField(required=False)
    difficulty = serializers.ChoiceField(
        choices=Word.DIFFICULTY_CHOICES, required=False
    )
    example_sentence = serializers.CharField(required=False, allow_blank=True)
    collocations = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    accepted_answers = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class DifficultWordSerializer(serializers.Serializer):
    """A word the student keeps getting wrong, with its failure rate."""

    id = serializers.IntegerField()
    word = serializers.CharField()
    times_wrong = serializers.IntegerField()
    review_count = serializers.IntegerField()
    failure_rate = serializers.IntegerField()


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
