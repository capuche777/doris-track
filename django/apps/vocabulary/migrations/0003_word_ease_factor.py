# Migration: DT-02 fix — add ease_factor field to Word model
# Bug: vocabulary/services.py accesses word.ease_factor but the field was missing
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vocabulary", "0002_word_times_wrong"),
    ]

    operations = [
        migrations.AddField(
            model_name="word",
            name="ease_factor",
            field=models.FloatField(
                default=2.5,
                help_text="SM-2 ease factor (starting at 2.5, adjusted by review quality)",
            ),
        ),
    ]