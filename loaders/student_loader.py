from models import db, Student
from utils.utils import (
    is_valid_email,
    is_valid_year,
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return,
    validate_required_fields
)

def validate_student(item):
    context = f"ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['nombre', 'correo', 'anio_ingreso'], context)
    if error:
        return None, error

    email = item.get('correo')
    if not is_valid_email(email):
        return None, standard_error(context, f"Correo inválido: {email}")

    admission_year = item.get('anio_ingreso')
    if not is_valid_year(admission_year):
        return None, standard_error(context, f"Año de ingreso fuera de rango: {admission_year}")

    student = Student(
        name=item['nombre'],
        email=email,
        admission_date=admission_year
    )
    return student, None

def import_students(data, force=False):
    students = data.get('alumnos', [])
    inserted = 0
    duplicated = []
    errors = []

    for item in students:
        student, error = validate_student(item)

        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        existing = Student.query.filter_by(email=student.email).first()

        if existing and not force:
            duplicated.append(format_duplicate(existing.__dict__, item, ['id', 'name', 'email', 'admission_date']))
            continue

        if existing and force:
            existing.name = item["nombre"]
            existing.email = item["correo"]
            existing.admission_date = item["anio_ingreso"]
            inserted += 1
            continue

        db.session.add(Student(
            id=item.get("id"),
            name=item["nombre"],
            email=item["correo"],
            admission_date=item["anio_ingreso"]
        ))
        inserted += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
