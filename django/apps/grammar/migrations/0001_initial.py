# Generated migration for grammar app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Correction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("student_mistake", models.TextField()),
                ("correct_version", models.TextField()),
                ("grammar_rule", models.TextField(blank=True)),
                ("category", models.CharField(choices=[("prepositions", "Prepositions"), ("verb_tenses", "Verb Tenses"), ("word_order", "Word Order"), ("articles", "Articles"), ("other", "Other")], default="other", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="grammar_corrections", to="profiles.student")),
            ],
            options={"ordering": ["-date"]},
        ),
    ]
