from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.entities import Section, Task, Student
from services.grade_service import get_students_in_section, update_grades_for_task, delete_grade_by_student_and_task, delete_all_grades_for_task
from models.validators import validate_grade_data, ValidationError
from utils.types_validators import validate_float

grades_bp = Blueprint('grades', __name__)

@grades_bp.route('/sections/<int:section_id>/tasks/<int:task_id>/grading', methods=['GET', 'POST'])
def grade_task(section_id, task_id):
    section = Section.query.get_or_404(section_id)
    task = Task.query.get_or_404(task_id)

    if task.evaluation.section_id != section_id:
        flash('Task does not belong to this section.', 'error')
        return redirect(url_for('sections.get_section_detail', section_id=section_id))

    students = get_students_in_section(section_id)

    if request.method == 'POST':
        try:
            for student in students:
                grade_value = request.form.get(f'grade_{student.id}')
                if grade_value:
                    validate_grade_data(
                        task_id=task_id,
                        student_id=student.id,
                        value=validate_float(grade_value, 'Grade value')
                    )
            
            update_grades_for_task(task_id, section_id, students, request.form)
            flash('Grades saved successfully!', 'success')
        except ValidationError as e:
            flash(str(e), 'error')
        except ValueError:
            flash('Invalid grade value', 'error')
        except Exception as e:
            flash('An error occurred while saving grades', 'error')
        
        return redirect(url_for('grades.grade_task', section_id=section_id, task_id=task_id))

    existing_grades = {g.student_id: g for g in task.grades}

    return render_template(
        'grades/task_grades.html',
        section=section,
        task=task,
        students=students,
        existing_grades=existing_grades
    )

@grades_bp.route('/sections/<int:section_id>/tasks/<int:task_id>/students/<int:student_id>/grade/delete', methods=['POST'])
def delete_student_grade(section_id, task_id, student_id):
    try:
        section = Section.query.get_or_404(section_id)
        task = Task.query.get_or_404(task_id)
        student = Student.query.get_or_404(student_id)
        
        if task.evaluation.section_id != section_id:
            flash('Task does not belong to this section.', 'error')
            return redirect(url_for('sections.get_section_detail', section_id=section_id))
        
        if delete_grade_by_student_and_task(student_id, task_id):
            flash(f'Nota de {student.name} eliminada exitosamente!', 'success')
        else:
            flash(f'No se encontró nota para {student.name}', 'warning')
            
    except Exception as e:
        flash('Error al eliminar la nota', 'error')
    
    return redirect(url_for('grades.grade_task', section_id=section_id, task_id=task_id))

@grades_bp.route('/sections/<int:section_id>/tasks/<int:task_id>/grades/delete-all', methods=['POST'])
def delete_all_task_grades(section_id, task_id):
    try:
        section = Section.query.get_or_404(section_id)
        task = Task.query.get_or_404(task_id)
        
        if task.evaluation.section_id != section_id:
            flash('Task does not belong to this section.', 'error')
            return redirect(url_for('sections.get_section_detail', section_id=section_id))
        
        count = delete_all_grades_for_task(task_id)
        
        if count > 0:
            flash(f'Se eliminaron {count} nota(s) exitosamente!', 'success')
        else:
            flash('No había notas para eliminar', 'info')
            
    except Exception as e:
        flash('Error al eliminar las notas', 'error')
    
    return redirect(url_for('grades.grade_task', section_id=section_id, task_id=task_id))
