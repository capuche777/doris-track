# Generated migration for vocabulary app — DT-02: add times_wrong field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vocabulary", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="word",
            name="times_wrong",
            field=models.IntegerField(default=0, help_text="Times student answered this word incorrectly"),
        ),
    ]
