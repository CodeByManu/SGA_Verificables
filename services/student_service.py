from models import db
from models.entities import Student

def get_all_students():
    return Student.query.all()

def get_student_by_id(student_id):
    return Student.query.get_or_404(student_id)

def create_student(form_data):
    try:
        name = form_data.get('name')
        email = form_data.get('email')
        admission_date = form_data.get('admission_date')

        if not name or not email or not admission_date:
            print("❌ Campos faltantes:", form_data)
            raise ValueError("Faltan campos obligatorios")

        
        student = Student(name=name, email=email, admission_date=admission_date)
        db.session.add(student)
        db.session.commit()

    except Exception as e:
        print(f"❌ Error al crear estudiante: {e}")
        raise  # 🔁 vuelve a lanzar el error si quieres que Flask lo muestre


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
