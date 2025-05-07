from .students import student_bp
from .teachers import teacher_bp
# Luego puedes agregar courses_bp, section_bp, etc.

__all__ = [
    "student_bp",
    "teacher_bp",
]
