"""Serializers for the practice API."""
from rest_framework import serializers

from apps.practice.models import PracticeSession


class PracticeSessionSerializer(serializers.ModelSerializer):
    """Full representation of a practice session."""

    class Meta:
        model = PracticeSession
        fields = [
            "id",
            "student",
            "date",
            "practice_type",
            "duration_minutes",
            "notes",
        ]


class PracticeCreateSerializer(serializers.Serializer):
    """Input payload for logging a practice session.

    ``date`` defaults to today when omitted.
    """

    practice_type = serializers.ChoiceField(
        choices=PracticeSession.PRACTICE_TYPE_CHOICES
    )
    duration_minutes = serializers.IntegerField(min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    date = serializers.DateField(required=False, default=None)


class PracticeStreakSerializer(serializers.Serializer):
    """Current consecutive-day practice streak."""

    streak = serializers.IntegerField()


class PracticeStatsSerializer(serializers.Serializer):
    """Aggregate practice statistics with per-type breakdown."""

    total_minutes = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    avg_duration = serializers.FloatField()
    by_type = serializers.DictField()
