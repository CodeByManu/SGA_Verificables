from flask import Blueprint, request, redirect, url_for, flash
from services.student_section_service import add_students_to_section, remove_student_from_section
student_section_bp = Blueprint('student_sections', __name__)

@student_section_bp.route('/sections/<int:section_id>/add_students', methods=['POST'])
def post_students_to_section(section_id):
    selected_ids = request.form.getlist('student_ids')
    added = add_students_to_section(section_id, selected_ids)
    flash(f'{added} estudiante(s) agregado(s) correctamente.')
    return redirect(url_for('sections.get_section_detail', section_id=section_id))



@student_section_bp.route('/sections/<int:section_id>/remove_student/<int:student_id>', methods=['POST'])
def remove_student_from_section_view(section_id, student_id):
    success = remove_student_from_section(section_id, student_id)
    if success:
        flash('Estudiante eliminado de la sección.', 'success')
    else:
        flash('No se encontró la asignación del estudiante.', 'danger')
    return redirect(url_for('sections.get_section_detail', section_id=section_id))


