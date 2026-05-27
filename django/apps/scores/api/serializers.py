"""Serializers for the scores API."""
from rest_framework import serializers

from apps.scores.models import Assessment, Score

VALID_SKILLS = {value for value, _ in Score.SKILL_CHOICES}


class AssessmentCreateSerializer(serializers.Serializer):
    """Input payload for recording an assessment with skill scores."""

    scores = serializers.DictField(
        child=serializers.IntegerField(min_value=0, max_value=100)
    )
    assessment_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_scores(self, value):
        if not value:
            raise serializers.ValidationError("At least one skill score is required.")
        invalid = set(value) - VALID_SKILLS
        if invalid:
            raise serializers.ValidationError(
                f"Invalid skill(s): {', '.join(sorted(invalid))}."
            )
        return value


class AssessmentSerializer(serializers.ModelSerializer):
    """Full representation of an assessment with its skill scores."""

    scores = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ["id", "student", "date", "notes", "scores"]

    def get_scores(self, obj) -> dict:
        return {s.skill: s.value for s in obj.scores.all()}


class ScoreHistoryItemSerializer(serializers.Serializer):
    """One assessment in a score-history listing."""

    assessment_id = serializers.IntegerField()
    date = serializers.DateField()
    scores = serializers.DictField(child=serializers.IntegerField())
