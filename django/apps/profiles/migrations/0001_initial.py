# Generated migration for profiles app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tutor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("current_level", models.CharField(choices=[("B1", "B1 - Intermediate"), ("B2", "B2 - Upper Intermediate"), ("C1", "C1 - Advanced"), ("C2", "C2 - Proficiency")], default="B1", max_length=2)),
                ("target_level", models.CharField(choices=[("B1", "B1 - Intermediate"), ("B2", "B2 - Upper Intermediate"), ("C1", "C1 - Advanced"), ("C2", "C2 - Proficiency")], default="C1", max_length=2)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("priority_areas", models.TextField(blank=True, help_text="Comma-separated: pronunciation, grammar, etc.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tutor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="students", to="profiles.tutor")),
            ],
            options={"ordering": ["name"]},
        ),
    ]
