"""Views for practice app — DT-08."""
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages

from apps.profiles.models import Student
from .models import PracticeSession
from .services import log_practice, get_practice_streak, get_practice_stats
from .selectors import get_sessions, get_heatmap_data


PRACTICE_TYPES = ["vocabulary", "writing", "idioms", "grammar", "conversation", "quiz"]


def practice_list_view(request):
    """Practice log: filterable table of sessions. DT-08."""
    student = Student.objects.first()
    if not student:
        return render(request, "practice/practice_list.html", {
            "sessions": [], "student": None, "streak": 0, "stats": {},
        })

    # Read filters
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    practice_type = request.GET.get("practice_type")

    sessions = get_sessions(student, date_from, date_to, practice_type)
    streak = get_practice_streak(student)
    stats = get_practice_stats(student)

    return render(request, "practice/practice_list.html", {
        "sessions": sessions,
        "student": student,
        "streak": streak,
        "stats": stats,
        "practice_types": PRACTICE_TYPES,
        "filters": {
            "date_from": date_from or "",
            "date_to": date_to or "",
            "practice_type": practice_type or "",
        },
    })


def practice_add_view(request):
    """Add a new practice session. DT-08."""
    student = Student.objects.first()
    if not student:
        return redirect("practice:practice_list")

    if request.method == "POST":
        practice_type = request.POST.get("practice_type")
        duration = request.POST.get("duration_minutes")
        notes = request.POST.get("notes", "")
        date_str = request.POST.get("date")

        if practice_type and duration:
            try:
                date_obj = date.fromisoformat(date_str) if date_str else date.today()
                log_practice(
                    student,
                    practice_type=practice_type,
                    duration_minutes=int(duration),
                    notes=notes,
                    date_obj=date_obj,
                )
                messages.success(request, "Practice session logged!")
                return redirect("practice:practice_list")
            except (ValueError, TypeError):
                messages.error(request, "Invalid data. Please check and try again.")

    return render(request, "practice/practice_add.html", {
        "student": student,
        "practice_types": PRACTICE_TYPES,
    })


def practice_heatmap_view(request):
    """GitHub-style contribution heatmap. DT-08."""
    student = Student.objects.first()
    if not student:
        return render(request, "practice/practice_heatmap.html", {
            "student": None, "heatmap_data": {}, "streak": 0, "year": date.today().year,
        })

    year = int(request.GET.get("year", date.today().year))
    heatmap_data = get_heatmap_data(student, year)
    streak = get_practice_streak(student)
    stats = get_practice_stats(student, days=365)

    return render(request, "practice/practice_heatmap.html", {
        "student": student,
        "heatmap_data": heatmap_data,
        "streak": streak,
        "stats": stats,
        "year": year,
        "years": [date.today().year - i for i in range(3)],
    })
