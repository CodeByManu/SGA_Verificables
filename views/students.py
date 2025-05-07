from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.student_service import (
    get_all_students,
    get_student_by_id,
    create_student,
    update_student,
    delete_student_by_id
)

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
    create_student(request.form)
    flash('Student added successfully!')
    return redirect(url_for('students.get_students'))

@student_bp.route('/students/<int:student_id>', methods=['POST'])
def update_student_view(student_id):
    update_student(student_id, request.form)
    flash('Student updated successfully!')
    return redirect(url_for('students.get_students'))

@student_bp.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    delete_student_by_id(student_id)
    flash('Student deleted successfully.')
    return redirect(url_for('students.get_students'))
