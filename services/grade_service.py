from flask import flash
from models import db
from models.entities import Student, StudentSection, Grade

def get_students_in_section(section_id):
    student_ids = [
        ss.student_id for ss in StudentSection.query.filter_by(section_id=section_id).all()
    ]
    return Student.query.filter(Student.id.in_(student_ids)).all()

def get_existing_grades(task_id):
    return {
        grade.student_id: grade for grade in Grade.query.filter_by(task_id=task_id).all()
    }

def update_grades_for_task(task_id, section_id, students, form_data):
    existing_grades = get_existing_grades(task_id)
    changes_made = False

    for student in students:
        key = f'grade_{student.id}'
        grade_value = form_data.get(key)

        if grade_value is not None:
            if grade_value.strip() == '':
                # Eliminar nota si existe
                if student.id in existing_grades:
                    db.session.delete(existing_grades[student.id])
                    changes_made = True
            else:
                try:
                    grade_value = float(grade_value)
                    if 0 <= grade_value <= 100:
                        if student.id in existing_grades:
                            existing_grades[student.id].value = grade_value
                        else:
                            new_grade = Grade(
                                value=grade_value,
                                student_id=student.id,
                                task_id=task_id
                            )
                            db.session.add(new_grade)
                        changes_made = True
                    else:
                        flash(f'La calificación para {student.name} debe estar entre 0 y 100.', 'warning')
                except ValueError:
                    flash(f'Valor inválido para la calificación de {student.name}.', 'warning')

    if changes_made:
        db.session.commit()
        return True
    return False
