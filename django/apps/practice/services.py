"""Service layer for practice app."""


def create_session(student, practice_type, duration_minutes, notes="", date=None):
    """Create a practice session."""
    from datetime import date as d
    if date is None:
        date = d.today()
    return PracticeSession.objects.create(
        student=student,
        date=date,
        practice_type=practice_type,
        duration_minutes=duration_minutes,
        notes=notes,
    )
