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
