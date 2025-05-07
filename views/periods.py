from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.period_service import (
    get_period_by_id,
    create_period_for_course,
    delete_period_by_id
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
    create_period_for_course(course_id, request.form)
    return redirect(url_for('courses.get_course_detail', course_id=course_id))

@period_bp.route('/courses/<int:course_id>/periods/<int:period_id>/delete', methods=['POST'])
def delete_period(course_id, period_id):
    delete_period_by_id(period_id)
    flash('Periodo eliminado correctamente.')
    return redirect(url_for('courses.get_course_detail', course_id=course_id))
