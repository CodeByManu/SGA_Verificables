from models import db
from models.entities import Student

def get_all_students():
    return Student.query.all()

def get_student_by_id(student_id):
    return Student.query.get_or_404(student_id)

def create_student(form_data):
    name = form_data.get('name')
    email = form_data.get('email')
    admission_date = form_data.get('admission_date')

    new_student = Student(name=name, email=email, admission_date=admission_date)
    db.session.add(new_student)
    db.session.commit()

def update_student(student_id, form_data):
    student = Student.query.get_or_404(student_id)
    student.name = form_data.get('name')
    student.email = form_data.get('email')
    student.admission_date = form_data.get('admission_date')
    db.session.commit()

def delete_student_by_id(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
