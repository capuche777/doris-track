"""Selectors for core app - aggregator functions for dashboard."""
from datetime import date, timedelta

from django.db import models

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
        "difficult_words": get_difficult_words(student),
        "grammar_alerts": get_grammar_alerts(student),
        "quiz_scores": get_quiz_scores(student),
        "next_quiz_date": get_next_quiz_date(student),
        "recent_corrections": get_recent_corrections(student),
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

    # Determine declining skills (latest below average) and per-skill trend
    # direction (latest score vs the previous one).
    declining_skills = []
    skill_trends = {}
    for skill, latest_value in latest_per_skill.items():
        skill_scores = list(
            Score.objects
            .filter(assessment__student=student, skill=skill)
            .order_by("assessment__date")
            .values_list("value", flat=True)
        )
        if len(skill_scores) >= 2:
            if skill_scores[-1] > skill_scores[-2]:
                skill_trends[skill] = "up"
            elif skill_scores[-1] < skill_scores[-2]:
                skill_trends[skill] = "down"
            else:
                skill_trends[skill] = "stable"
            avg = sum(skill_scores) / len(skill_scores)
            if latest_value < avg:
                declining_skills.append(skill)
        else:
            skill_trends[skill] = "stable"

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
        "skill_trends": skill_trends,
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
    today = date.today()
    sessions = (
        PracticeSession.objects
        .filter(student=student)
        .order_by("-date")
        .values_list("date", flat=True)
        .distinct()
    )
    dates = list(sessions)
    if not dates:
        return {"streak": 0, "last_practice": None, "minutes_this_week": 0, "sessions_last_30_days": 0}

    last_practice = dates[0]
    streak = 0
    check_date = today

    # Count consecutive days backwards from today
    for d in sorted(dates, reverse=True):
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d - timedelta(days=1)
        else:
            break

    week_start = today - timedelta(days=today.weekday())
    minutes_this_week = (
        PracticeSession.objects
        .filter(student=student, date__gte=week_start)
        .aggregate(total=models.Sum("duration_minutes"))["total"] or 0
    )

    return {
        "streak": streak,
        "last_practice": last_practice.isoformat() if last_practice else None,
        "sessions_last_30_days": len([d for d in dates if d >= date.today() - timedelta(days=30)]),
        "minutes_this_week": minutes_this_week,
    }


def get_difficult_words(student, limit=5):
    """Return top `limit` most-missed words (highest times_wrong)."""
    words = (
        Word.objects
        .filter(student=student, times_wrong__gt=0)
        .order_by("-times_wrong")[:limit]
    )
    return [
        {"word": w.word, "times_wrong": w.times_wrong, "mastery": w.mastery}
        for w in words
    ]


def get_grammar_alerts(student, limit=3):
    """Return top `limit` most common grammar mistakes this month."""
    from apps.grammar.models import Correction
    month_start = date.today().replace(day=1)
    corrections = (
        Correction.objects
        .filter(student=student, date__gte=month_start)
        .values("category")
        .annotate(count=models.Count("id"))
        .order_by("-count")[:limit]
    )
    return [
        {"category": c["category"], "count": c["count"]}
        for c in corrections
    ]


def get_recent_corrections(student, limit=10):
    """Return last `limit` grammar corrections."""
    from apps.grammar.models import Correction
    corrections = Correction.objects.filter(student=student).order_by("-date")[:limit]
    return [
        {
            "date": c.date.isoformat(),
            "mistake": c.student_mistake,
            "correct": c.correct_version,
            "rule": c.grammar_rule,
            "category": c.category,
        }
        for c in corrections
    ]


def get_quiz_scores(student, limit=3):
    """Return last `limit` quizzes with their score as a percentage."""
    from apps.quiz.models import Quiz
    quizzes = (
        Quiz.objects
        .filter(student=student)
        .prefetch_related("questions")
        .order_by("-week_start_date")[:limit]
    )
    result = []
    for q in quizzes:
        questions = q.questions.all()
        total = len(questions)
        correct = sum(1 for question in questions if question.is_correct)
        score_percent = round(correct / total * 100) if total else None
        result.append({
            "week_start_date": q.week_start_date.isoformat(),
            "score_percent": score_percent,
        })
    return result


def get_next_quiz_date(student):
    """Return the upcoming quiz date (next Monday from today)."""
    from apps.quiz.models import Quiz
    today = date.today()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_until_monday)
    # Check if quiz exists for that week
    existing = Quiz.objects.filter(student=student, week_start_date=next_monday).exists()
    return {"next_quiz_date": next_monday.isoformat(), "scheduled": existing}
