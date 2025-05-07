from models import db
from models.entities import Teacher

def get_all_teachers():
    return Teacher.query.all()

def get_teacher_by_id(teacher_id):
    return Teacher.query.get_or_404(teacher_id)

def create_teacher(form_data):
    name = form_data.get('name')
    email = form_data.get('email')
    new_teacher = Teacher(name=name, email=email)
    db.session.add(new_teacher)
    db.session.commit()

def update_teacher(teacher_id, form_data):
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher.name = form_data.get('name')
    teacher.email = form_data.get('email')
    db.session.commit()

def delete_teacher_by_id(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
