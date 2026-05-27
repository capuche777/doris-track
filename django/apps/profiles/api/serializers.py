"""Serializers for the profiles API."""
from rest_framework import serializers

from apps.profiles.models import Student


class StudentSerializer(serializers.ModelSerializer):
    """Public representation of a student for the Doris bot."""

    priority_areas = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "email",
            "current_level",
            "target_level",
            "start_date",
            "priority_areas",
        ]

    def get_priority_areas(self, obj) -> list:
        """Expose the comma-separated text field as a list of strings."""
        return [area.strip() for area in obj.priority_areas.split(",") if area.strip()]
