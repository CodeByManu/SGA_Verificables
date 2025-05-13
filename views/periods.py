from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.period_service import (
    get_period_by_id,
    create_period_for_course,
    delete_period_by_id,
    update_period
)
from models.entities import Teacher  # Necesario para mostrar en detalle
from models.validators import validate_period_data, ValidationError

period_bp = Blueprint('periods', __name__)

@period_bp.route('/periods/<int:period_id>', methods=['GET'])
def get_period_detail(period_id):
    period = get_period_by_id(period_id)
    teachers = Teacher.query.all()
    return render_template('periods/period_detail.html', period=period, teachers=teachers, active_page='courses')

@period_bp.route('/courses/<int:course_id>/periods', methods=['POST'])
def post_period(course_id):
    try:
        period_value = request.form.get('period')
        # Validate period data
        validate_period_data(
            course_id=course_id,
            period=period_value
        )
        
        create_period_for_course(course_id, period_value)
        flash('Period added successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('An error occurred while creating the period', 'error')
    
    return redirect(url_for('courses.get_course_detail', course_id=course_id))

@period_bp.route('/courses/<int:course_id>/periods/<int:period_id>/delete', methods=['POST'])
def delete_period(course_id, period_id):
    try:
        delete_period_by_id(period_id)
        flash('Period deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the period', 'error')
    
    return redirect(url_for('courses.get_course_detail', course_id=course_id))

@period_bp.route('/courses/<int:course_id>/periods/<int:period_id>', methods=['POST'])
def update_period_view(course_id, period_id):
    try:
        period_value = request.form.get('period')
        # Validate period data
        validate_period_data(
            course_id=course_id,
            period=period_value
        )
        
        update_period(period_id, request.form)
        flash('Period updated successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('An error occurred while updating the period', 'error')
    
    return redirect(url_for('courses.get_course_detail', course_id=course_id))
