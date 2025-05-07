from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.period_service import (
    get_period_by_id,
    create_period_for_course,
    delete_period_by_id,
    update_period
)
from models.entities import Teacher  # Necesario para mostrar en detalle

period_bp = Blueprint('periods', __name__)

@period_bp.route('/periods/<int:period_id>', methods=['GET'])
def get_period_detail(period_id):
    period = get_period_by_id(period_id)
    teachers = Teacher.query.all()
    return render_template('periods/period_detail.html', period=period, teachers=teachers, active_page='courses')

@period_bp.route('/courses/<int:course_id>/periods', methods=['POST'])
def post_period(course_id):
    period_value = request.form.get('period')
    if period_value:
        create_period_for_course(course_id, period_value)
        flash('Periodo agregado correctamente.')
    else:
        flash('Debes ingresar un nombre de periodo.')
    return redirect(url_for('courses.get_course_detail', course_id=course_id))

@period_bp.route('/courses/<int:course_id>/periods/<int:period_id>/delete', methods=['POST'])
def delete_period(course_id, period_id):
    delete_period_by_id(period_id)
    flash('Periodo eliminado correctamente.')
    return redirect(url_for('courses.get_course_detail', course_id=course_id))

@period_bp.route('/courses/<int:course_id>/periods/<int:period_id>', methods=['POST'])
def update_period_view(course_id, period_id):
    success = update_period(period_id, request.form)
    if success:
        flash('Periodo actualizado correctamente.')
    else:
        flash('El valor del periodo no puede estar vacío.', 'warning')
    return redirect(url_for('courses.get_course_detail', course_id=course_id))
