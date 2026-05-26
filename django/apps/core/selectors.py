"""Selectors for core app - aggregator functions for dashboard."""
from datetime import date, timedelta

from apps.profiles.models import Student
from apps.scores.models import Assessment, Score
from apps.vocabulary.models import Word
from apps.practice.models import PracticeSession


def get_student_by_request(request):
    """Get student from request - uses email from authenticated user or session."""
    if hasattr(request, "user") and request.user.is_authenticated:
        return Student.objects.filter(email=request.user.email).first()
    # Fallback: first student (for demo purposes)
    return Student.objects.first()


def get_student_dashboard_data(student):
    """
    Aggregate all DorisTrack data for a student's main dashboard.
    Returns dict with score_summary, vocabulary_stats, practice_streak, etc.
    """
    if not student:
        return None

    return {
        "student_info": get_student_info(student),
        "score_summary": get_score_summary(student),
        "vocabulary_stats": get_vocabulary_stats(student),
        "practice_streak": get_practice_streak(student),
    }


def get_student_info(student):
    """Return student name, levels, tutor."""
    return {
        "name": student.name,
        "current_level": student.current_level,
        "target_level": student.target_level,
        "tutor": student.tutor.name if student.tutor else None,
    }


def get_score_summary(student, limit=5):
    """
    Return latest `limit` assessments with scores per skill.
    Also highlight skills that are declining (score trending down).
    """
    assessments = (
        Assessment.objects
        .filter(student=student)
        .prefetch_related("scores")
        .order_by("-date")[:limit]
    )

    # Build latest_per_skill from all assessments
    latest_per_skill = {}
    for skill, _ in Score.SKILL_CHOICES:
        score = (
            Score.objects
            .filter(assessment__student=student, skill=skill)
            .order_by("-assessment__date")
            .first()
        )
        if score:
            latest_per_skill[skill] = score.value

    # Determine declining skills (latest score below average)
    declining_skills = []
    for skill, latest_value in latest_per_skill.items():
        skill_scores = list(
            Score.objects
            .filter(assessment__student=student, skill=skill)
            .order_by("assessment__date")
            .values_list("value", flat=True)
        )
        if len(skill_scores) >= 2:
            avg = sum(skill_scores) / len(skill_scores)
            if latest_value < avg:
                declining_skills.append(skill)

    return {
        "latest_assessments": [
            {
                "id": a.id,
                "date": a.date.isoformat(),
                "notes": a.notes,
                "scores": {s.skill: s.value for s in a.scores.all()},
            }
            for a in assessments
        ],
        "latest_per_skill": latest_per_skill,
        "declining_skills": declining_skills,
    }


def get_vocabulary_stats(student):
    """Return total words, breakdown by mastery, words due today."""
    total_words = Word.objects.filter(student=student).count()
    new_count = Word.objects.filter(student=student, mastery="new").count()
    learning_count = Word.objects.filter(student=student, mastery="learning").count()
    mastered_count = Word.objects.filter(student=student, mastery="mastered").count()
    due_today = Word.objects.filter(
        student=student,
        next_review_date__lte=date.today(),
    ).exclude(mastery="mastered").count()

    return {
        "total_words": total_words,
        "new": new_count,
        "learning": learning_count,
        "mastered": mastered_count,
        "words_due_today": due_today,
    }


def get_practice_streak(student):
    """
    Calculate current practice streak (consecutive days with practice).
    Returns streak count and last practice date.
    """
    sessions = (
        PracticeSession.objects
        .filter(student=student)
        .order_by("-date")
        .values_list("date", flat=True)
        .distinct()
    )
    dates = list(sessions)
    if not dates:
        return {"streak": 0, "last_practice": None}

    last_practice = dates[0]
    streak = 0
    check_date = date.today()

    # Count consecutive days backwards from today
    for d in sorted(dates, reverse=True):
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d - timedelta(days=1)
        else:
            break

    # Alternative: simple count of sessions in last N days
    # Just count distinct days in last 30
    recent_sessions = [
        d for d in dates
        if d >= date.today() - timedelta(days=30)
    ]

    return {
        "streak": streak,
        "last_practice": last_practice.isoformat() if last_practice else None,
        "sessions_last_30_days": len(recent_sessions),
    }