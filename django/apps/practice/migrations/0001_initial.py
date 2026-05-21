# Generated migration for practice app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
        ("vocabulary", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PracticeSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("practice_type", models.CharField(choices=[("vocabulary", "Vocabulary"), ("writing", "Writing"), ("idioms", "Idioms"), ("grammar", "Grammar"), ("conversation", "Conversation"), ("quiz", "Quiz")], max_length=20)),
                ("duration_minutes", models.IntegerField(default=0)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="practice_sessions", to="profiles.student")),
                ("words_learned", models.ManyToManyField(blank=True, related_name="practice_sessions", to="vocabulary.word")),
            ],
            options={"ordering": ["-date"]},
        ),
    ]
