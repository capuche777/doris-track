# Generated manually for scores app (Task #223 / DT-04)
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assessments", to="profiles.student")),
            ],
            options={"ordering": ["-date"], "verbose_name_plural": "assessments"},
        ),
        migrations.CreateModel(
            name="Score",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("skill", models.CharField(choices=[("pronunciation", "Pronunciation"), ("fluency", "Fluency"), ("intonation", "Intonation"), ("grammar", "Grammar"), ("vocabulary", "Vocabulary")], max_length=20)),
                ("value", models.IntegerField()),
                ("assessment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scores", to="scores.assessment")),
            ],
            options={"ordering": ["skill"], "unique_together": {("assessment", "skill")}},
        ),
    ]