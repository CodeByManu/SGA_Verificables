from datetime import datetime
import re
from typing import Optional, Union
from .entities import db, Course, Student, Teacher, Section, Period, Evaluation, Task, Grade, StudentSection

class ValidationError(Exception):
    pass

def validate_email(email: str) -> bool:

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    return True

def validate_course_data(code: str, name: str, credits: Optional[int] = None, course_id: Optional[int] = None) -> bool:

    if not code or not name:
        raise ValidationError("Code and name are required")
    
    if credits is not None and credits <= 0:
        raise ValidationError("Credits must be a positive number")
    
    # Check if code is unique
    existing_course = Course.query.filter_by(code=code).first()
    if existing_course and (course_id is None or existing_course.id != course_id):
        raise ValidationError("Course code must be unique")
    
    return True

def validate_student_data(name: str, email: str, admission_date: int, student_id: Optional[int] = None) -> bool:

    if not name or not name.strip():
        raise ValidationError("Name is required")
    
    validate_email(email)
    
    # Check if email is unique
    existing_student = Student.query.filter_by(email=email).first()
    if existing_student and (student_id is None or existing_student.id != student_id):
        raise ValidationError("Email must be unique")
    
    current_year = datetime.now().year
    if not (2000 <= admission_date <= current_year):
        raise ValidationError("Invalid admission date")
    
    return True

def validate_teacher_data(name: str, email: str, teacher_id: Optional[int] = None) -> bool:

    if not name:
        raise ValidationError("Name is required")
    
    validate_email(email)
    
    # Check if email is unique
    existing_teacher = Teacher.query.filter_by(email=email).first()
    if existing_teacher and (teacher_id is None or existing_teacher.id != teacher_id):
        raise ValidationError("Email must be unique")
    
    return True

def validate_section_data(period_id: int, teacher_id: int, section_number: str, section_id: Optional[int] = None) -> bool:

    if not section_number:
        raise ValidationError("Section number is required")
    
    # Check if period exists
    period = Period.query.get(period_id)
    if not period:
        raise ValidationError("Period does not exist")
    
    # Check if teacher exists
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        raise ValidationError("Teacher does not exist")
    
    # Check if section number is unique for the period
    existing_section = Section.query.filter_by(
        period_id=period_id,
        section_number=section_number
    ).first()
    if existing_section and (section_id is None or existing_section.id != section_id):
        raise ValidationError("Section number must be unique for the period")
    
    return True

def validate_evaluation_data(name: str, section_id: int, weight: float) -> bool:
 
    if not name:
        raise ValidationError("Name is required")
    
    # Check if section exists
    section = Section.query.get(section_id)
    if not section:
        raise ValidationError("Section does not exist")
    
    if not (0 <= weight <= 100):
        raise ValidationError("Weight must be between 0 and 100")
    
    return True

def validate_task_data(name: str, evaluation_id: int, date: datetime.date, weight: Optional[float] = None) -> bool:

    if not name:
        raise ValidationError("Name is required")
    
    # Check if evaluation exists
    evaluation = Evaluation.query.get(evaluation_id)
    if not evaluation:
        raise ValidationError("Evaluation does not exist")
    
    if weight is not None and not (0 <= weight <= 100):
        raise ValidationError("Weight must be between 0 and 100")
    
    if date < datetime.now().date():
        raise ValidationError("Task date cannot be in the past")
    
    return True

def validate_grade_data(task_id: int, student_id: int, value: float) -> bool:

    # Check if task exists
    task = Task.query.get(task_id)
    if not task:
        raise ValidationError("Task does not exist")
    
    # Check if student exists
    student = Student.query.get(student_id)
    if not student:
        raise ValidationError("Student does not exist")
    
    # Check if student is enrolled in the section
    student_section = StudentSection.query.filter_by(
        student_id=student_id,
        section_id=task.evaluation.section_id
    ).first()
    if not student_section:
        raise ValidationError("Student is not enrolled in this section")
    
    if not (0 <= value <= 100):
        raise ValidationError("Grade value must be between 0 and 100")
    
    return True

def validate_student_section_data(student_id: int, section_id: int) -> bool:
 
    # Check if student exists
    student = Student.query.get(student_id)
    if not student:
        raise ValidationError("Student does not exist")
    
    # Check if section exists
    section = Section.query.get(section_id)
    if not section:
        raise ValidationError("Section does not exist")
    
    # Check for duplicate enrollment
    existing_enrollment = StudentSection.query.filter_by(
        student_id=student_id,
        section_id=section_id
    ).first()
    if existing_enrollment:
        raise ValidationError("Student is already enrolled in this section")
    
    return True

def validate_period_data(course_id: int, period: str, period_id: Optional[int] = None) -> bool:

    if not period:
        raise ValidationError("Period is required")
    
    # Check if course exists
    course = Course.query.get(course_id)
    if not course:
        raise ValidationError("Course does not exist")
    
    # Check if period is unique for the course
    existing_period = Period.query.filter_by(
        course_id=course_id,
        period=period
    ).first()
    if existing_period and (period_id is None or existing_period.id != period_id):
        raise ValidationError("Period must be unique for the course")
    
    return True