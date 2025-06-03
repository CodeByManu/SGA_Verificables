from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.course_service import (
    get_all_courses,
    get_course_by_id,
    create_course,
    update_course,
    delete_course_by_id
)
from models.validators import validate_course_data, ValidationError
from utils.types_validators import validate_integer, validate_required_string

course_bp = Blueprint('courses', __name__)

@course_bp.route('/courses', methods=['GET'])
def get_courses():
    courses = get_all_courses()
    return render_template('courses/courses.html', courses=courses, active_page='courses')

@course_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course_detail(course_id):
    course = get_course_by_id(course_id)
    return render_template('courses/course_detail.html', course=course, active_page='courses')

@course_bp.route('/courses', methods=['POST'])
def post_course():
    try:
        validate_course_data(
            code=validate_required_string(request.form.get('code'), 'Course code'),
            name=validate_required_string(request.form.get('name'), 'Course name'),
            credits=validate_integer(request.form.get('credits'), 'Credits')
        )
        
        create_course(request.form)
        flash('Course added successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid credits value', 'error')
    except Exception as e:
        flash('An error occurred while creating the course', 'error')
    
    return redirect(url_for('courses.get_courses'))

@course_bp.route('/courses/<int:course_id>', methods=['POST'])
def update_course_view(course_id):
    try:
        validate_course_data(
            code=validate_required_string(request.form.get('code'), 'Course code'),
            name=validate_required_string(request.form.get('name'), 'Course name'),
            credits=validate_integer(request.form.get('credits'), 'Credits'),
            course_id=course_id
        )
        update_course(course_id, request.form)
        flash('Course updated successfully!', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except ValueError:
        flash('Invalid credits value', 'error')
    except Exception as e:
        flash('An error occurred while updating the course', 'error')
    
    return redirect(url_for('courses.get_courses'))

@course_bp.route('/course/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    try:
        delete_course_by_id(course_id)
        flash('Course deleted successfully.', 'success')
    except Exception as e:
        flash('An error occurred while deleting the course', 'error')
    
    return redirect(url_for('courses.get_courses'))
