from flask import Blueprint, request, redirect, url_for, flash
from services.student_section_service import add_students_to_section
from models.entities import Section

student_section_bp = Blueprint('student_sections', __name__)

@student_section_bp.route('/sections/<int:section_id>/add_students', methods=['POST'])
def add_students_to_section_view(section_id):
    section = Section.query.get_or_404(section_id)
    selected_ids = request.form.getlist('student_ids')

    added = add_students_to_section(section.id, selected_ids)
    flash(f'{added} estudiante(s) agregado(s) correctamente.')
    return redirect(url_for('sections.get_section_detail', section_id=section.id))
