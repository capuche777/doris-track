"""Views for scores app."""
import json
from datetime import date

from django.shortcuts import render, redirect
from django.contrib import messages

from apps.profiles.models import Student
from .models import Assessment, Score
from .services import record_assessment, detect_declining_skills
from .selectors import get_assessments, get_latest_scores


SKILL_COLORS = {
    "pronunciation": "#3B82F6",  # blue
    "fluency": "#22C55E",        # green
    "intonation": "#F97316",      # orange
    "grammar": "#EF4444",         # red
    "vocabulary": "#A855F7",     # purple
}


def score_list_view(request):
    """List all assessments for the student."""
    student = Student.objects.first()
    if not student:
        return render(request, "scores/score_list.html", {"student": None, "assessments": []})

    assessments = get_assessments(student.id)
    latest = get_latest_scores(student.id)
    declines = detect_declining_skills(student.id)

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

    # Collect all dates across all skills
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
        # Map date -> value for quick lookup
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

    chart_data = {
        "labels": date_labels,
        "datasets": chart_datasets,
    }

    return render(request, "scores/score_charts.html", {
        "student": student,
        "latest": latest,
        "decline_warning": bool(declines),
        "decline_skills": declines,
        "chart_data": json.dumps(chart_data),
    })