# Data migration: backfill accepted_answers for known prefix/tag mismatches.
from django.db import migrations


# Suggested defaults from docs/spec-accepted-answers.md, keyed by word text.
SUGGESTED_ACCEPTED_ANSWERS = {
    "to shut down": ["shut down"],
    "to sit tight": ["sit tight"],
    "to choke": ["choke"],
    "to keep at bay": ["keep at bay"],
    "to drive crazy": ["drive crazy"],
    "to tell time": ["tell time"],
    "to dot": ["dot"],
    "to strike": ["strike"],
    "to assess": ["assess"],
    "to commit": ["commit"],
    "to unleash": ["unleash"],
    "to turn out": ["turn out"],
    "that being said": ["that said", "having said that"],
}


def apply_defaults(apps, schema_editor):
    """Set suggested accepted_answers on matching words that have none yet."""
    Word = apps.get_model("vocabulary", "Word")
    for word_text, accepted in SUGGESTED_ACCEPTED_ANSWERS.items():
        for word in Word.objects.filter(word=word_text):
            if not word.accepted_answers:
                word.accepted_answers = accepted
                word.save(update_fields=["accepted_answers"])


def clear_defaults(apps, schema_editor):
    """Revert words still holding exactly the suggested defaults."""
    Word = apps.get_model("vocabulary", "Word")
    for word_text, accepted in SUGGESTED_ACCEPTED_ANSWERS.items():
        for word in Word.objects.filter(word=word_text):
            if word.accepted_answers == accepted:
                word.accepted_answers = []
                word.save(update_fields=["accepted_answers"])


class Migration(migrations.Migration):

    dependencies = [
        ("vocabulary", "0005_word_accepted_answers"),
    ]

    operations = [
        migrations.RunPython(apply_defaults, clear_defaults),
    ]
