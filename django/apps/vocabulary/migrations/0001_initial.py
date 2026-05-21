# Generated migration for vocabulary app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Word",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("word", models.CharField(max_length=255)),
                ("definition", models.TextField()),
                ("difficulty", models.CharField(choices=[("B2", "B2 - Upper Intermediate"), ("C1", "C1 - Advanced"), ("C2", "C2 - Proficiency")], default="B2", max_length=2)),
                ("example_sentence", models.TextField(blank=True)),
                ("collocations", models.TextField(blank=True, help_text="Common collocations")),
                ("date_learned", models.DateField(blank=True, null=True)),
                ("review_count", models.IntegerField(default=0)),
                ("mastery", models.CharField(choices=[("new", "New"), ("learning", "Learning"), ("mastered", "Mastered")], default="new", max_length=10)),
                ("next_review_date", models.DateField(blank=True, null=True)),
                ("current_interval_days", models.IntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="words", to="profiles.student")),
            ],
            options={"ordering": ["word"]},
        ),
    ]
