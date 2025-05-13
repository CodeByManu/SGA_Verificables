from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.teacher_service import (
    get_all_teachers,
    get_teacher_by_id,
    create_teacher,
    update_teacher,
    delete_teacher_by_id
)
from models.validators import validate_teacher_data, ValidationError

teacher_bp = Blueprint('teachers', __name__)

@teacher_bp.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = get_all_teachers()
    return render_template('teachers/teachers.html', teachers=teachers, active_page='teachers')

@teacher_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher_detail(teacher_id):
    teacher = get_teacher_by_id(teacher_id)
    return render_template('teachers/teacher_detail.html', teacher=teacher, active_page='teachers')

@teacher_bp.route('/teachers', methods=['POST'])
def post_teacher():
    try:
        # Validate teacher data
        validate_teacher_data(
            name=request.form.get('name'),
            email=request.form.get('email')
        )
        
        create_teacher(request.form)
        flash('Teacher added successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('An error occurred while creating the teacher', 'error')
    
    return redirect(url_for('teachers.get_teachers'))

@teacher_bp.route('/teachers/<int:teacher_id>', methods=['POST'])
def update_teacher_view(teacher_id):
    try:
        # Validate teacher data
        validate_teacher_data(
            name=request.form.get('name'),
            email=request.form.get('email')
        )
        
        update_teacher(teacher_id, request.form)
        flash('Teacher updated successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('An error occurred while updating the teacher', 'error')
    
    return redirect(url_for('teachers.get_teachers'))

@teacher_bp.route('/teacher/delete/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    try:
        delete_teacher_by_id(teacher_id)
        flash('Teacher deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the teacher', 'error')
    
    return redirect(url_for('teachers.get_teachers'))
