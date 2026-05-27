"""Service layer for practice app — DT-08."""
from datetime import date, timedelta
from collections import defaultdict
from .models import PracticeSession


def log_practice(student, practice_type: str, duration_minutes: int, notes: str = "", date_obj: date = None) -> PracticeSession:
    """
    Log a new practice session. DT-08.
    Returns the created PracticeSession instance.
    """
    if date_obj is None:
        date_obj = date.today()
    return PracticeSession.objects.create(
        student=student,
        practice_type=practice_type,
        duration_minutes=duration_minutes,
        notes=notes,
        date=date_obj,
    )


def get_practice_streak(student) -> int:
    """
    Calculate the current consecutive-day practice streak for a student.
    Counts days with at least one practice session, ending at today.
    DT-08.
    """
    today = date.today()
    streak = 0
    check_date = today

    # If no practice today, start checking from yesterday
    has_today = PracticeSession.objects.filter(student=student, date=today).exists()
    if not has_today:
        check_date = today - timedelta(days=1)

    # Walk backwards counting consecutive days
    while True:
        if PracticeSession.objects.filter(student=student, date=check_date).exists():
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak


def get_practice_breakdown(student, days: int = 30) -> dict:
    """
    Get aggregate practice statistics with per-type session and minute counts.
    Returns: {total_minutes, total_sessions, avg_duration,
              by_type: {type: {sessions, minutes}}}
    """
    start = date.today() - timedelta(days=days)
    sessions = PracticeSession.objects.filter(student=student, date__gte=start)

    total_minutes = sum(s.duration_minutes for s in sessions)
    total_sessions = sessions.count()
    avg_duration = round(total_minutes / total_sessions, 1) if total_sessions > 0 else 0

    by_type = defaultdict(lambda: {"sessions": 0, "minutes": 0})
    for s in sessions:
        by_type[s.practice_type]["sessions"] += 1
        by_type[s.practice_type]["minutes"] += s.duration_minutes

    return {
        "total_minutes": total_minutes,
        "total_sessions": total_sessions,
        "avg_duration": avg_duration,
        "by_type": {k: dict(v) for k, v in by_type.items()},
    }


def get_practice_stats(student, days: int = 30) -> dict:
    """
    Get aggregate practice statistics for the student over the last N days. DT-08.
    Returns: {total_minutes, total_sessions, avg_duration, by_type: {type: minutes}}
    """
    data = get_practice_breakdown(student, days)
    data["by_type"] = {k: v["minutes"] for k, v in data["by_type"].items()}
    return data
