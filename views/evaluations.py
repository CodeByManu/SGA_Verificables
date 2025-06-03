from flask import Blueprint, request, redirect, url_for, flash
from services.evaluation_service import (
    create_evaluation_for_section,
    delete_evaluation_by_id,
    update_evaluation
)
from models.entities import Evaluation
from models.validators import validate_evaluation_data, ValidationError
from utils.types_validators import validate_float, validate_required_string

evaluation_bp = Blueprint('evaluations', __name__)

@evaluation_bp.route('/sections/<int:section_id>/evaluations', methods=['POST'])
def post_evaluation(section_id):
    try:
        name = validate_required_string(request.form.get('name'), 'Evaluation name')
        weight = validate_float(request.form.get('weight'), 'Evaluation weight')
        validate_evaluation_data(name, section_id, weight)
        
        create_evaluation_for_section(section_id, request.form)
        flash('Evaluation created successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid weight value', 'error')
    except Exception as e:
        flash('An error occurred while creating the evaluation', 'error')
    
    return redirect(url_for('sections.get_section_detail', section_id=section_id))

@evaluation_bp.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>', methods=['POST'])
def update_evaluation_view(section_id, evaluation_id):
    try:
        name = validate_required_string(request.form.get('name'), 'Evaluation name')
        weight = validate_float(request.form.get('weight'), 'Evaluation weight')
        validate_evaluation_data(name, section_id, weight)
        
        update_evaluation(evaluation_id, request.form)
        flash('Evaluation updated successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid weight value', 'error')
    except Exception as e:
        flash('An error occurred while updating the evaluation', 'error')
    
    return redirect(url_for('sections.get_section_detail', section_id=section_id))

@evaluation_bp.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/delete', methods=['POST'])
def delete_evaluation(section_id, evaluation_id):
    try:
        delete_evaluation_by_id(evaluation_id)
        flash('Evaluation deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the evaluation', 'error')
    
    return redirect(url_for('sections.get_section_detail', section_id=section_id))
