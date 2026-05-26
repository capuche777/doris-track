"""Practice app models."""
from django.db import models


class PracticeSession(models.Model):
    """Record of a practice session."""
    PRACTICE_TYPE_CHOICES = [
        ("vocabulary", "Vocabulary"),
        ("writing", "Writing"),
        ("idioms", "Idioms"),
        ("grammar", "Grammar"),
        ("conversation", "Conversation"),
        ("quiz", "Quiz"),
    ]

    student = models.ForeignKey(
        "profiles.Student", on_delete=models.CASCADE, related_name="practice_sessions"
    )
    date = models.DateField()
    practice_type = models.CharField(max_length=20, choices=PRACTICE_TYPE_CHOICES)
    duration_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    words_learned = models.ManyToManyField(
        "vocabulary.Word", blank=True, related_name="practice_sessions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.practice_type} on {self.date}"
