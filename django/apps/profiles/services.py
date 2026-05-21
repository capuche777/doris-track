"""Service layer for profiles app."""


def get_or_create_student(name: str, email: str, **kwargs):
    """Get existing student or create new one."""
    from .models import Student
    student, created = Student.objects.get_or_create(email=email, defaults={"name": name, **kwargs})
    return student, created
