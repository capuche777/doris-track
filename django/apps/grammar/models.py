"""Grammar app models."""
from django.db import models


class Correction(models.Model):
    """Grammar correction log entry."""
    CATEGORY_CHOICES = [
        ("prepositions", "Prepositions"),
        ("verb_tenses", "Verb Tenses"),
        ("word_order", "Word Order"),
        ("articles", "Articles"),
        ("other", "Other"),
    ]

    student = models.ForeignKey(
        "profiles.Student", on_delete=models.CASCADE, related_name="grammar_corrections"
    )
    date = models.DateField()
    student_mistake = models.TextField()
    correct_version = models.TextField()
    grammar_rule = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Correction #{self.id} [{self.category}]"
