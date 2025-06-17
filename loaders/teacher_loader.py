from models import db, Teacher
from utils.utils import (
    standard_error,
    validate_required_fields,
    format_duplicate,
    safe_commit,
    standard_return
)
from utils.types_validators import (
    validate_email_format,
    validate_required_string,
    validate_id_parameter,
    FormValidationError
)

def validate_teachers_data(data):
    if not isinstance(data, dict):
        return None, ["El archivo debe ser un objeto JSON"]

    teachers = data.get('profesores')
    if not isinstance(teachers, list):
        return None, ["El campo 'profesores' debe ser una lista de objetos"]

    return teachers, None


def process_teacher_entry(item, force):
    context = f"ID {item.get('id') or 'N/A'}"

    valid_data, error = validate_required_fields(item, ['nombre', 'correo'], context)
    if error:
        return None, None, error

    try:
        teacher_id = item.get("id")
        if teacher_id is not None:
            validate_id_parameter(teacher_id, "ID")

        name = validate_required_string(item["nombre"], "Nombre")
        email = validate_email_format(item["correo"], "Correo")

        existing = Teacher.query.filter_by(email=email).first()

        if existing and not force:
            return None, format_duplicate(existing.__dict__, item, ['id', 'name', 'email']), None

        if existing and force:
            existing.name = name
            existing.email = email
            return 'updated', None, None

        teacher = Teacher(id=teacher_id, name=name, email=email)
        db.session.add(teacher)
        return 'inserted', None, None

    except FormValidationError as e:
        return None, None, standard_error(context, str(e))


def import_teachers(data, force=False):
    teachers, structure_errors = validate_teachers_data(data)
    if structure_errors:
        return standard_return(errors=structure_errors)

    inserted = 0
    updated = 0
    duplicated = []
    errors = []

    for item in teachers:
        result, duplicate_info, error = process_teacher_entry(item, force)

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
