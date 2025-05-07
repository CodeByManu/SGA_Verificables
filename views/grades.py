from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.entities import Section, Task
from services.grade_service import get_students_in_section, update_grades_for_task

grades_bp = Blueprint('grades', __name__)

@grades_bp.route('/sections/<int:section_id>/tasks/<int:task_id>/grading', methods=['GET', 'POST'])
def task_grading(section_id, task_id):
    section = Section.query.get_or_404(section_id)
    task = Task.query.get_or_404(task_id)

    if task.evaluation.section_id != section_id:
        flash('La tarea no pertenece a esta sección.', 'danger')
        return redirect(url_for('sections.get_section_detail', section_id=section_id))

    students = get_students_in_section(section_id)

    if request.method == 'POST':
        success = update_grades_for_task(task_id, section_id, students, request.form)
        if success:
            flash('Calificaciones guardadas correctamente.', 'success')
        return redirect(url_for('grades.task_grading', section_id=section_id, task_id=task_id))

    existing_grades = {g.student_id: g for g in task.grades}

    return render_template(
        'grades/task_grades.html',
        section=section,
        task=task,
        students=students,
        existing_grades=existing_grades
    )
