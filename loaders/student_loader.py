from models import db, Student
from utils.utils import (
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return,
    validate_required_fields
)
from utils.types_validators import (
    validate_email_format,
    validate_integer,
    validate_required_string,
    validate_id_parameter,
    FormValidationError
)

def validate_students_data(data):
    if not isinstance(data, dict):
        return None, ["El archivo debe ser un objeto JSON"]

    students = data.get('alumnos')
    if not isinstance(students, list):
        return None, ["El campo 'alumnos' debe ser una lista de objetos"]

    return students, None


def process_student_entry(item, force):
    context = f"ID {item.get('id') or 'N/A'}"

    valid_data, error = validate_required_fields(item, ['nombre', 'correo', 'anio_ingreso'], context)
    if error:
        return None, None, error

    try:
        student_id = item.get("id")
        if student_id is not None:
            validate_id_parameter(student_id, "ID")

        name = validate_required_string(item["nombre"], "Nombre")
        email = validate_email_format(item["correo"], "Correo")
        admission_year = validate_integer(item["anio_ingreso"], "Año de ingreso", min_val=1940, max_val=2025)

        existing = Student.query.filter_by(email=email).first()

        if existing and not force:
            return None, format_duplicate(existing.__dict__, item, ['id', 'name', 'email', 'admission_date']), None

        if existing and force:
            existing.name = name
            existing.email = email
            existing.admission_date = admission_year
            return 'updated', None, None

        student = Student(
            id=student_id,
            name=name,
            email=email,
            admission_date=admission_year
        )
        db.session.add(student)
        return 'inserted', None, None

    except FormValidationError as e:
        return None, None, standard_error(context, str(e))


def import_students(data, force=False):
    students, structure_errors = validate_students_data(data)
    if structure_errors:
        return standard_return(errors=structure_errors)

    inserted = 0
    updated = 0
    duplicated = []
    errors = []

    for item in students:
        result, duplicate_info, error = process_student_entry(item, force)

        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        if duplicate_info:
            duplicated.append(duplicate_info)
            continue

        if result == 'inserted':
            inserted += 1
        elif result == 'updated':
            updated += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
