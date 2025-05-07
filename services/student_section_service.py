from models import db
from models.entities import StudentSection

def add_students_to_section(section_id, student_ids):
    """
    Agrega una lista de estudiantes a una sección, evitando duplicados.
    Retorna el número de estudiantes efectivamente agregados.
    """
    count = 0
    for student_id in student_ids:
        exists = StudentSection.query.filter_by(
            student_id=student_id,
            section_id=section_id
        ).first()
        if not exists:
            db.session.add(StudentSection(student_id=student_id, section_id=section_id))
            count += 1

    if count > 0:
        db.session.commit()
    return count
