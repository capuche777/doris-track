"""Quiz app models."""
from django.db import models
from django.utils import timezone


class Quiz(models.Model):
    """Weekly quiz."""
    student = models.ForeignKey(
        "apps.profiles.Student", on_delete=models.CASCADE, related_name="quizzes"
    )
    week_start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-week_start_date"]
        unique_together = ["student", "week_start_date"]

    def __str__(self):
        return f"Quiz {self.week_start_date}"


class QuizQuestion(models.Model):
    """Individual question in a quiz."""
    QUESTION_TYPE_CHOICES = [
        ("definition_to_word", "Definition to Word"),
        ("word_to_sentence", "Word to Sentence"),
        ("sentence_rewrite", "Sentence Rewrite"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    prompt = models.TextField()
    correct_answer = models.TextField()
    student_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Question {self.id} [{self.question_type}]"
