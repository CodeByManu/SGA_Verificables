from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.section_service import (
    get_section_by_id,
    create_section_for_period,
    delete_section_by_id,
    update_section,
    get_section_and_available_students
)
from models.validators import validate_section_data, ValidationError

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
    try:
        validate_section_data(
            period_id=period_id,
            teacher_id=int(request.form.get('teacher_id')),
            section_number=request.form.get('section_number')
        )
        
        create_section_for_period(period_id, request.form)
        flash('Section created successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid teacher ID', 'error')
    except Exception as e:
        flash('An error occurred while creating the section', 'error')
    
    return redirect(url_for('periods.get_period_detail', period_id=period_id))

@section_bp.route('/periods/<int:period_id>/sections/<int:section_id>/delete', methods=['POST'])
def delete_section(period_id, section_id):
    try:
        delete_section_by_id(section_id)
        flash('Section deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the section', 'error')
    
    return redirect(url_for('periods.get_period_detail', period_id=period_id))

@section_bp.route('/periods/<int:period_id>/sections/<int:section_id>', methods=['POST'])
def update_section_view(period_id, section_id):
    try:
        validate_section_data(
            period_id=period_id,
            teacher_id=int(request.form.get('teacher_id')),
            section_number=request.form.get('section_number'),
            section_id=section_id
        )
        
        update_section(section_id, request.form)
        flash('Section updated successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid teacher ID', 'error')
    except Exception as e:
        flash('An error occurred while updating the section', 'error')
    
    return redirect(url_for('periods.get_period_detail', period_id=period_id))
