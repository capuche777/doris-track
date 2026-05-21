"""Students app models."""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    """Student profile linked to Django User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    display_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.display_name or self.user.username


class Word(models.Model):
    """Vocabulary word in the bank."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="words")
    term = models.CharField(max_length=255)
    definition = models.TextField()
    example_sentence = models.TextField(blank=True)
    language = models.CharField(max_length=20, default="en")
    tags = models.CharField(max_length=255, blank=True)  # comma-separated
    times_correct = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)  # SM-2 algorithm
    interval_days = models.IntegerField(default=1)
    next_review_date = models.DateField(null=True, blank=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["term"]

    def __str__(self):
        return self.term

    @property
    def accuracy(self):
        total = self.times_correct + self.times_incorrect
        if total == 0:
            return 0
        return round(self.times_correct / total * 100, 1)


class Score(models.Model):
    """Daily score record."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="scores")
    date = models.DateField()
    total_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=100)
    quiz_count = models.IntegerField(default=0)
    words_reviewed = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        unique_together = ["student", "date"]

    def __str__(self):
        return f"{self.student.user.username} - {self.date} ({self.total_score})"


class Quiz(models.Model):
    """Quiz session record."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="quizzes")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Quiz {self.id} - {self.student.user.username}"


class GrammarCorrection(models.Model):
    """Grammar correction log entry."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grammar_corrections")
    original_text = models.TextField()
    corrected_text = models.TextField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Grammar #{self.id} - {self.student.user.username}"