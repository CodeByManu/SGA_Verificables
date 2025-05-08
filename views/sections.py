from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.section_service import (
    get_section_by_id,
    create_section_for_period,
    delete_section_by_id,
    update_section,
    get_section_and_available_students
)

section_bp = Blueprint('sections', __name__)

@section_bp.route('/sections/<int:section_id>')
def get_section_detail(section_id):
    section, available_students, now = get_section_and_available_students(section_id)
    return render_template(
        'sections/section_detail.html',
        section=section,
        available_students=available_students,
        active_page='courses',
        now=now
    )

@section_bp.route('/periods/<int:period_id>/sections', methods=['POST'])
def post_section(period_id):
    create_section_for_period(period_id, request.form)
    return redirect(url_for('periods.get_period_detail', period_id=period_id))

@section_bp.route('/periods/<int:period_id>/sections/<int:section_id>/delete', methods=['POST'])
def delete_section(period_id, section_id):
    delete_section_by_id(section_id)
    flash('Sección eliminada correctamente.')
    return redirect(url_for('periods.get_period_detail', period_id=period_id))

@section_bp.route('/periods/<int:period_id>/sections/<int:section_id>', methods=['POST'])
def update_section_view(period_id, section_id):
    success = update_section(section_id, request.form)
    if success:
        flash('Sección actualizada correctamente.', 'success')
    else:
        flash('Todos los campos son obligatorios.', 'warning')
    return redirect(url_for('periods.get_period_detail', period_id=period_id))
