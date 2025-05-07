from .students import student_bp
from .teachers import teacher_bp
from .courses import course_bp  
from .periods import period_bp

__all__ = [
    "student_bp",
    "teacher_bp",
    "course_bp",
    "period_bp"
]