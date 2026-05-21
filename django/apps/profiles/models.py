"""Profiles app models."""
from django.db import models


class Tutor(models.Model):
    """Tutor/teacher profile."""
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    """Student profile."""
    LEVEL_CHOICES = [
        ("B1", "B1 - Intermediate"),
        ("B2", "B2 - Upper Intermediate"),
        ("C1", "C1 - Advanced"),
        ("C2", "C2 - Proficiency"),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    current_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default="B1")
    target_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default="C1")
    start_date = models.DateField(null=True, blank=True)
    priority_areas = models.TextField(blank=True, help_text="Comma-separated: pronunciation, grammar, etc.")
    tutor = models.ForeignKey(
        Tutor, on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.current_level} → {self.target_level})"