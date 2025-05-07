from flask import Blueprint, request, redirect, url_for, flash
from services.task_service import create_task, delete_task_by_id

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/tasks', methods=['POST'])
def add_task_to_evaluation(section_id, evaluation_id):
    success = create_task(evaluation_id, request.form)
    if success:
        flash('Tarea agregada correctamente.')
    return redirect(url_for('sections.get_section_detail', section_id=section_id))

@task_bp.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(section_id, evaluation_id, task_id):
    delete_task_by_id(task_id)
    flash('Tarea eliminada correctamente.')
    return redirect(url_for('sections.get_section_detail', section_id=section_id))
