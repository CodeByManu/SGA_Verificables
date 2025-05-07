from models import db
from models.entities import Course

def get_all_courses():
    return Course.query.all()

def get_course_by_id(course_id):
    return Course.query.get_or_404(course_id)

def create_course(form_data):
    code = form_data.get('code')
    name = form_data.get('name')
    description = form_data.get('description')

    new_course = Course(code=code, name=name, description=description)
    db.session.add(new_course)
    db.session.commit()

def update_course(course_id, form_data):
    course = Course.query.get_or_404(course_id)
    course.code = form_data.get('code')
    course.name = form_data.get('name')
    course.description = form_data.get('description')
    db.session.commit()

def delete_course_by_id(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
