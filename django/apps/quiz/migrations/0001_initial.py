# Generated migration for quiz app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Quiz",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("week_start_date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quizzes", to="profiles.student")),
            ],
            options={"ordering": ["-week_start_date"]},
        ),
        migrations.CreateModel(
            name="QuizQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_type", models.CharField(choices=[("definition_to_word", "Definition to Word"), ("word_to_sentence", "Word to Sentence"), ("sentence_rewrite", "Sentence Rewrite")], max_length=20)),
                ("prompt", models.TextField()),
                ("correct_answer", models.TextField()),
                ("student_answer", models.TextField(blank=True)),
                ("is_correct", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("quiz", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="quiz.quiz")),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.AddConstraint(
            model_name="quiz",
            constraint=models.UniqueConstraint(fields=("student", "week_start_date"), name="unique_student_week"),
        ),
    ]
