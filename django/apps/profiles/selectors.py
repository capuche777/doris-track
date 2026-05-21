from apps.profiles.models import Student


def get_student_profile(student_id):
    """Get student profile by ID. Returns None if not found."""
    try:
        return Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return None