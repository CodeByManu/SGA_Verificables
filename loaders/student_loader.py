from models import db, Student

def validate_student(item):
    student_id = item.get('id')
    name = item.get('nombre')
    email = item.get('correo')
    admission_date = item.get('anio_ingreso')

    if not name or not email or not admission_date:
        return None, f"ID {student_id or 'N/A'}: Missing required fields."

    if '@' not in email:
        return None, f"ID {student_id or 'N/A'}: Invalid email address: {email}"

    if not (1940 <= int(admission_date) <= 2025):
        return None, f"ID {student_id or 'N/A'}: Admission year out of range: {admission_date}"

    return Student(name=name, email=email, admission_date=admission_date), None

def handle_student_duplicates(existing, item):
    return {
        "ya_existe": {
            "id": existing.id,
            "name": existing.name,
            "email": existing.email,
            "admission_date": existing.admission_date
        },
        "nuevo": {
            "id": item.get('id'),
            "name": item.get('nombre'),
            "email": item.get('email'),
            "admission_date": item.get('anio_ingreso')
        }
    }

def import_students(data, force=False):
    students = data.get('alumnos', [])  # ✅ español
    inserted = 0
    duplicated = []
    mistakes = []

    for item in students:
        student, error = validate_student(item)

        if error:
            mistakes.append(error)
            continue

        existing = Student.query.filter_by(email=student.email).first()

        if existing and not force:
            duplicated.append(handle_student_duplicates(existing, item))
            continue

        if existing and force:
            db.session.delete(existing)
            db.session.flush()

        db.session.add(student)
        inserted += 1

    db.session.commit()
    return {
        "inserted": inserted,
        "ignored": len(mistakes),
        "duplicated": duplicated,
        "mistakes": mistakes
    }
