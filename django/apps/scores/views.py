"""Views for scores app."""
import json
from datetime import date, timedelta

from django.db.models import Avg
from django.shortcuts import render, redirect
from django.contrib import messages

from apps.profiles.models import Student
from .models import Assessment, Score
from .services import record_assessment, detect_declining_skills
from .selectors import get_assessments, get_latest_scores, get_score_trends


SKILL_COLORS = {
    "pronunciation": "#3B82F6",  # blue
    "fluency": "#22C55E",        # green
    "intonation": "#F97316",      # orange
    "grammar": "#EF4444",         # red
    "vocabulary": "#A855F7",     # purple
}


def _get_trends(student_id: int) -> dict:
    """
    Compute trend direction per skill: 'up', 'down', or 'stable'.
    Compares last 7 days avg vs previous 7 days avg.
    """
    today = date.today()
    recent_start = today - timedelta(days=6)
    previous_start = today - timedelta(days=13)
    previous_end = today - timedelta(days=7)

    trends = {}
    for skill, _ in Score.SKILL_CHOICES:
        recent = Score.objects.filter(
            assessment__student_id=student_id,
            skill=skill,
            assessment__date__range=(recent_start, today),
        ).aggregate(avg=Avg("value"))["avg"]

        previous = Score.objects.filter(
            assessment__student_id=student_id,
            skill=skill,
            assessment__date__range=(previous_start, previous_end),
        ).aggregate(avg=Avg("value"))["avg"]

        if recent is None or previous is None:
            trends[skill] = "stable"
        elif recent - previous >= 3:
            trends[skill] = "up"
        elif previous - recent >= 3:
            trends[skill] = "down"
        else:
            trends[skill] = "stable"
    return trends


def score_list_view(request):
    """List all assessments for the student."""
    student = Student.objects.first()
    if not student:
        return render(request, "scores/score_list.html", {"student": None, "assessments": []})

    assessments = get_assessments(student.id)
    latest = get_latest_scores(student.id)
    declines = detect_declining_skills(student.id)
    trends = _get_trends(student.id)

    # Build latest scores dict with skill ordering
    assessment_data = []
    for a in assessments:
        score_dict = {s.skill: s.value for s in a.scores.all()}
        assessment_data.append({"date": a.date, "scores": score_dict})

    return render(request, "scores/score_list.html", {
        "student": student,
        "assessments": assessments,
        "latest": latest,
        "decline_warning": bool(declines),
        "decline_skills": declines,
        "assessment_data": assessment_data,
        "skill_colors": SKILL_COLORS,
        "trends": trends,
    })


def score_entry_view(request):
    """Form to record a new assessment."""
    student = Student.objects.first()
    if not student:
        return render(request, "scores/score_entry.html", {
            "student": None,
            "skills": list(SKILL_COLORS.keys()),
        })

    declines = detect_declining_skills(student.id)

    if request.method == "POST":
        scores_dict = {}
        for skill in SKILL_COLORS:
            val = request.POST.get(f"score_{skill}")
            if val is not None and val.strip():
                try:
                    scores_dict[skill] = int(val)
                except ValueError:
                    pass

        assessment_date_str = request.POST.get("assessment_date")
        notes = request.POST.get("notes", "")

        try:
            assessment_date = date.fromisoformat(assessment_date_str) if assessment_date_str else date.today()
        except ValueError:
            assessment_date = date.today()

        if scores_dict:
            record_assessment(student.id, scores_dict, assessment_date, notes)
            messages.success(request, "Assessment recorded!")
            return redirect("scores:score_list")
        else:
            messages.error(request, "Please enter at least one score.")

    return render(request, "scores/score_entry.html", {
        "student": student,
        "skills": list(SKILL_COLORS.keys()),
        "decline_warning": bool(declines),
        "decline_skills": declines,
        "today": date.today().isoformat(),
    })


def score_charts_view(request):
    """Chart.js visualization of score history."""
    student = Student.objects.first()
    if not student:
        return render(request, "scores/score_charts.html", {"student": None, "chart_data": None})

    latest = get_latest_scores(student.id)
    declines = detect_declining_skills(student.id)

    # Compute baseline (overall average across all scores for each date range)
    all_scores_qs = (
        Score.objects
        .filter(assessment__student_id=student.id)
        .order_by("assessment__date")
        .select_related("assessment")
    )

    # Collect unique sorted dates
    date_vals = sorted(set(s.assessment.date for s in all_scores_qs))
    date_labels = [d.isoformat() for d in date_vals]

    # Build one dataset per skill
    chart_datasets = []
    for skill, color in SKILL_COLORS.items():
        skill_qs = all_scores_qs.filter(skill=skill)
        date_to_value = {s.assessment.date: s.value for s in skill_qs}
        values = [date_to_value.get(d, None) for d in date_vals]
        chart_datasets.append({
            "label": skill.capitalize(),
            "data": values,
            "borderColor": color,
            "backgroundColor": color + "33",
            "fill": False,
            "tension": 0.3,
            "pointRadius": 4,
        })

    # Baseline: average of all scores across all skills for each date (fixed N+1)
    baseline_aggr = (
        Score.objects
        .filter(assessment__student_id=student.id)
        .values("assessment__date")
        .annotate(avg=Avg("value"))
        .order_by("assessment__date")
    )
    date_to_avg = {row["assessment__date"]: row["avg"] for row in baseline_aggr}
    baseline_values = [round(date_to_avg.get(d, 0) or 0, 1) if d in date_to_avg else None for d in date_vals]

    chart_datasets.append({
        "label": "Baseline",
        "data": baseline_values,
        "borderColor": "#6B7280",
        "borderDash": [5, 5],
        "backgroundColor": "transparent",
        "fill": False,
        "tension": 0,
        "pointRadius": 0,
        "borderWidth": 2,
    })

    # Declining zones: annotate red background bands for the specific date range of decline
    # The "decline" is calculated over last 7 days vs previous 7 days, so mark recent 7 days
    annotations = {}
    if declines:
        today = date.today()
        recent_start = today - timedelta(days=6)
        recent_end = today
        for skill, info in declines.items():
            color = SKILL_COLORS.get(skill, "#EF4444")
            # Find index range in date_labels for the declining period
            xMin_idx = None
            xMax_idx = None
            for i, d in enumerate(date_vals):
                if recent_start <= d <= recent_end:
                    if xMin_idx is None:
                        xMin_idx = i
                    xMax_idx = i
            if xMin_idx is not None and xMax_idx is not None:
                annotations[f"decline_{skill}"] = {
                    "type": "box",
                    "xMin": xMin_idx,
                    "xMax": xMax_idx,
                    "backgroundColor": color + "22",
                    "borderColor": "transparent",
                    "borderWidth": 0,
                }

    chart_data = {
        "labels": date_labels,
        "datasets": chart_datasets,
        "annotations": annotations,
    }

    return render(request, "scores/score_charts.html", {
        "student": student,
        "latest": latest,
        "decline_warning": bool(declines),
        "decline_skills": declines,
        "chart_data": json.dumps(chart_data),
    })
