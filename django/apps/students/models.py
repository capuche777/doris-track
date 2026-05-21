"""Students app models — simplified, delegates to profiles app."""
from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    """Student profile linked to Django User (legacy, for User.auth)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.user.username