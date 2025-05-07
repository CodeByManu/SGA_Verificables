from flask import Blueprint, request, redirect, url_for, flash
from services.evaluation_service import (
    create_evaluation_for_section,
    delete_evaluation_by_id
)
from models.entities import Evaluation

evaluation_bp = Blueprint('evaluations', __name__)

@evaluation_bp.route('/sections/<int:section_id>/evaluations', methods=['POST'])
def post_evaluation(section_id):
    form_data = request.form
    if create_evaluation_for_section(section_id, form_data):
        flash('Evaluación creada correctamente.')
    else:
        flash('Todos los campos son obligatorios.')
    return redirect(url_for('sections.get_section_detail', section_id=section_id))

@evaluation_bp.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/delete', methods=['POST'])
def delete_evaluation(section_id, evaluation_id):
    delete_evaluation_by_id(evaluation_id)
    flash('Evaluación eliminada correctamente.')
    return redirect(url_for('sections.get_section_detail', section_id=section_id))
