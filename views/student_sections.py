from flask import Blueprint, request, redirect, url_for, flash
from services.student_section_service import add_students_to_section, remove_student_from_section
from models.validators import validate_student_section_data, ValidationError

student_section_bp = Blueprint('student_sections', __name__)

@student_section_bp.route('/sections/<int:section_id>/add_students', methods=['POST'])
def post_students_to_section(section_id):
    try:
        selected_ids = request.form.getlist('student_ids')
        added_count = 0
        
        for student_id in selected_ids:
            try:
                # Validate each student-section relationship
                validate_student_section_data(
                    student_id=int(student_id),
                    section_id=section_id
                )
                added_count += 1
            except ValidationError as e:
                flash(f'Error with student {student_id}: {str(e)}', 'error')
                continue
        
        if added_count > 0:
            add_students_to_section(section_id, selected_ids)
            flash(f'{added_count} student(s) added successfully!', 'success')
        else:
            flash('No students were added.', 'warning')
            
    except Exception as e:
        flash('An error occurred while adding students to the section', 'error')
    
    return redirect(url_for('sections.get_section_detail', section_id=section_id))

@student_section_bp.route('/sections/<int:section_id>/remove_student/<int:student_id>', methods=['POST'])
def remove_student_from_section_view(section_id, student_id):
    try:
        success = remove_student_from_section(section_id, student_id)
        if success:
            flash('Student removed from section successfully.', 'success')
        else:
            flash('Student enrollment not found.', 'error')
    except Exception as e:
        flash('An error occurred while removing the student from the section', 'error')
    
    return redirect(url_for('sections.get_section_detail', section_id=section_id))


