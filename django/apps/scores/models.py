"""Scores app models."""
from django.db import models
from apps.profiles.models import Student


class Assessment(models.Model):
    """A single assessment session with scores across multiple skills."""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="assessments"
    )
    date = models.DateField()
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "assessments"

    def __str__(self):
        return f"Assessment {self.student.name} — {self.date}"


class Score(models.Model):
    """A single skill score within an assessment."""

    SKILL_CHOICES = [
        ("pronunciation", "Pronunciation"),
        ("fluency", "Fluency"),
        ("intonation", "Intonation"),
        ("grammar", "Grammar"),
        ("vocabulary", "Vocabulary"),
    ]

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="scores"
    )
    skill = models.CharField(max_length=20, choices=SKILL_CHOICES)
    value = models.IntegerField()  # 0–100

    class Meta:
        ordering = ["skill"]
        unique_together = [["assessment", "skill"]]

    def __str__(self):
        return f"{self.skill}: {self.value}/100"