from django.db import models


class Student(models.Model):
    """Single student model — no user authentication."""

    name = models.CharField(max_length=200)
    start_date = models.DateField(auto_now_add=True)
    current_level = models.CharField(max_length=50, default="A1")
    target_level = models.CharField(max_length=50, default="B2")
    priority_areas = models.JSONField(default=list)  # list of strings

    def __str__(self):
        return self.name