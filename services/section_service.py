from models import db
from models.entities import Section, Student, Teacher
from datetime import datetime
from services.final_grade_service import calculate_final_grades

def get_all_sections():
    return Section.query.all()

def get_section_by_id(section_id):
    return Section.query.get_or_404(section_id)

def create_section_for_period(period_id, form_data):
    section_number = form_data.get('section_number')
    teacher_id = form_data.get('teacher_id')
    evaluation_weight_type = form_data.get('evaluation_weight_type')

    teacher = Teacher.query.get(teacher_id)
    if section_number and teacher:
        new_section = Section(
            period_id=period_id,
            section_number=section_number,
            teacher_id=teacher.id,
            evaluation_weight_type=evaluation_weight_type,
            open=True
        )
        db.session.add(new_section)
        db.session.commit()

def update_section(section_id, form_data):
    section = Section.query.get_or_404(section_id)

    if not section.open:
        raise ValueError("No se puede modificar una sección cerrada.")

    section_number = form_data.get('section_number')
    teacher_id = form_data.get('teacher_id')
    evaluation_weight_type = form_data.get('evaluation_weight_type')

    if section_number and teacher_id and evaluation_weight_type:
        section.section_number = section_number
        section.teacher_id = teacher_id
        section.evaluation_weight_type = evaluation_weight_type
        db.session.commit()
        return True
    return False


def get_section_and_available_students(section_id):
    section = Section.query.get_or_404(section_id)
    current_ids = [ss.student_id for ss in section.student_sections]
    available_students = Student.query.filter(Student.id.notin_(current_ids)).all()
    return section, available_students, datetime.now().date()

def delete_section_by_id(section_id):
    section = Section.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()

def close_section(section_id):
    section = Section.query.get_or_404(section_id)

    if not section.open:
        raise ValueError("Section is already closed.")

    section.open = False
    db.session.commit()
    calculate_final_grades(section_id)
