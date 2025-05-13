from models import db
from models.entities import StudentSection

# CORRECTO

def get_all_student_section():
    return StudentSection.query.all()

def add_students_to_section(section_id, student_ids):
    for student_id in student_ids:
        exists = StudentSection.query.filter_by(
            student_id=student_id,
            section_id=section_id
        ).first()
        if not exists:
            db.session.add(StudentSection(student_id=student_id, section_id=section_id))
    db.session.commit()
    return len(student_ids)

def remove_student_from_section(section_id, student_id):
    ss = StudentSection.query.filter_by(section_id=section_id, student_id=student_id).first()
    if ss:
        db.session.delete(ss)
        db.session.commit()
        return True
    return False
