"""Service layer for grammar app."""


def log_correction(student, mistake, correct, rule="", category="other"):
    """Log a grammar correction entry."""
    from datetime import date
    from .models import Correction
    return Correction.objects.create(
        student=student,
        date=date.today(),
        student_mistake=mistake,
        correct_version=correct,
        grammar_rule=rule,
        category=category,
    )
