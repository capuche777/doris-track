"""Vocabulary app models."""
from datetime import date

from django.db import models


class Word(models.Model):
    """Vocabulary word with spaced repetition fields."""
    MASTERY_CHOICES = [
        ("new", "New"),
        ("learning", "Learning"),
        ("mastered", "Mastered"),
    ]
    DIFFICULTY_CHOICES = [
        ("B2", "B2 - Upper Intermediate"),
        ("C1", "C1 - Advanced"),
        ("C2", "C2 - Proficiency"),
    ]

    student = models.ForeignKey(
        "profiles.Student", on_delete=models.CASCADE, related_name="words"
    )
    word = models.CharField(max_length=255)
    definition = models.TextField()
    difficulty = models.CharField(max_length=2, choices=DIFFICULTY_CHOICES, default="B2")
    example_sentence = models.TextField(blank=True)
    collocations = models.TextField(blank=True, help_text="Common collocations")
    date_learned = models.DateField(null=True, blank=True)
    review_count = models.IntegerField(default=0)
    mastery = models.CharField(max_length=10, choices=MASTERY_CHOICES, default="new")
    next_review_date = models.DateField(null=True, blank=True, default=date.today)
    times_wrong = models.IntegerField(default=0, help_text="Times student answered this word incorrectly")
    ease_factor = models.FloatField(default=2.5, help_text="SM-2 ease factor (starting at 2.5, adjusted by review quality)")
    current_interval_days = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["word"]
        unique_together = [["student", "word"]]

    def __str__(self):
        return self.word
