"""Dashboard views - main student dashboard."""
from django.shortcuts import render

from apps.core.selectors import get_student_by_request, get_student_dashboard_data


def dashboard(request):
    """Main student dashboard - aggregates all DorisTrack modules."""
    student = get_student_by_request(request)
    data = get_student_dashboard_data(student)
    return render(request, "dashboard/dashboard.html", {"dashboard": data, "student": student})