from flask import Blueprint, request, redirect, url_for, flash
from services.task_service import create_task, delete_task_by_id
from models.validators import validate_task_data, ValidationError
from datetime import datetime

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/tasks', methods=['POST'])
def add_task_to_evaluation(section_id, evaluation_id):
    try:
        validate_task_data(
            name=request.form.get('name'),
            evaluation_id=evaluation_id,
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            weight=float(request.form.get('weight')) if request.form.get('weight') else None
        )
        
        create_task(evaluation_id, request.form)
        flash('Task added successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid date or weight value', 'error')
    except Exception as e:
        flash('An error occurred while creating the task', 'error')
    
    return redirect(url_for('sections.get_section_detail', section_id=section_id))

@task_bp.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(section_id, evaluation_id, task_id):
    try:
        delete_task_by_id(task_id)
        flash('Task deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the task', 'error')
    
    return redirect(url_for('sections.get_section_detail', section_id=section_id))
