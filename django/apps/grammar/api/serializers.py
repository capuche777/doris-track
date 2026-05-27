"""Serializers for the grammar API."""
from rest_framework import serializers

from apps.grammar.models import Correction


class CorrectionCreateSerializer(serializers.ModelSerializer):
    """Input payload for logging a grammar correction.

    ``student`` and ``date`` are set by the service, not the client.
    """

    class Meta:
        model = Correction
        fields = ["student_mistake", "correct_version", "grammar_rule", "category"]


class CorrectionSerializer(serializers.ModelSerializer):
    """Full representation of a logged correction."""

    class Meta:
        model = Correction
        fields = [
            "id",
            "student",
            "date",
            "student_mistake",
            "correct_version",
            "grammar_rule",
            "category",
        ]


class MistakeCategorySerializer(serializers.Serializer):
    """A grammar mistake category ranked by frequency."""

    category = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()
    example = serializers.CharField()


class MistakeTrendPointSerializer(serializers.Serializer):
    """Weekly mistake count for a category."""

    week_start = serializers.CharField()
    count = serializers.IntegerField()
