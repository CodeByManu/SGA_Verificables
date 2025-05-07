from .students import student_bp
from .teachers import teacher_bp
from .courses import course_bp
from .periods import period_bp
from .sections import section_bp
from .evaluations import evaluation_bp
from .grades import grades_bp
from .tasks import task_bp
from .student_sections import student_section_bp
from .home import home_bp

__all__ = [
    "student_bp",
    "teacher_bp",
    "course_bp",
    "period_bp",
    "section_bp",
    "evaluation_bp",
    "grades_bp",
    "task_bp",
    "student_section_bp",
    "home_bp"
]
