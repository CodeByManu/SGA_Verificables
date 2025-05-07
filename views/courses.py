from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.course_service import (
    get_all_courses,
    get_course_by_id,
    create_course,
    update_course,
    delete_course_by_id
)

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
    create_course(request.form)
    flash('Course added successfully!')
    return redirect(url_for('courses.get_courses'))

@course_bp.route('/courses/<int:course_id>', methods=['POST'])
def update_course_view(course_id):
    update_course(course_id, request.form)
    flash('Course updated successfully!')
    return redirect(url_for('courses.get_courses'))

@course_bp.route('/course/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    delete_course_by_id(course_id)
    flash('Course deleted successfully.')
    return redirect(url_for('courses.get_courses'))
