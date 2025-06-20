from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.student_service import (
    get_all_students,
    get_student_by_id,
    create_student,
    update_student,
    delete_student_by_id
)
from models.validators import validate_student_data, ValidationError
from utils.types_validators import validate_date, validate_email_format, validate_required_string, validate_integer

student_bp = Blueprint('students', __name__)

@student_bp.route('/students', methods=['GET'])
def get_students():
    students = get_all_students()
    return render_template('students/students.html', students=students, active_page='students')

@student_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student_detail(student_id):
    student = get_student_by_id(student_id)
    return render_template('students/student_detail.html', student=student, active_page='students')

@student_bp.route('/students', methods=['POST'])
def post_student():
    try:
        
        name = validate_required_string(request.form.get('name'), 'Student name')
        email = validate_email_format(request.form.get('email'), 'Student email')
        admission_date = validate_integer(request.form.get('admission_date'), 'Admission date')
        validate_student_data(name, email, admission_date)
        create_student(request.form)
        flash('Student created successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid admission date value', 'error')
    except Exception as e:
        flash('An error occurred while creating the student', 'error')
    
    return redirect(url_for('students.get_students'))

@student_bp.route('/students/<int:student_id>', methods=['POST'])
def update_student_view(student_id):
    try:
        name = validate_required_string(request.form.get('name'), 'Student name')
        email = validate_email_format(request.form.get('email'), 'Student email')
        admission_date = validate_date(request.form.get('admission_date'), 'Admission date')
        validate_student_data(name, email, admission_date, student_id)
        
        update_student(student_id, request.form)
        flash('Student updated successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid admission date value', 'error')
    except Exception as e:
        flash('An error occurred while updating the student', 'error')
    
    return redirect(url_for('students.get_students'))

@student_bp.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        delete_student_by_id(student_id)
        flash('Student deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the student', 'error')
    
    return redirect(url_for('students.get_students'))
