from models import db, Classroom
from utils.utils import (
    validate_required_fields,
    standard_error,
    safe_commit,
    standard_return,
    format_duplicate
)
from utils.types_validators import (
    validate_required_string,
    validate_id_parameter,
    validate_integer,
    FormValidationError
)

def validate_classrooms_data(data):
    if not isinstance(data, dict):
        return None, ["El archivo debe ser un objeto JSON"]

    classrooms = data.get("salas")
    if not isinstance(classrooms, list):
        return None, ["El campo 'salas' debe ser una lista de objetos"]

    return classrooms, None

def validate_classroom(item):
    context = f"Sala ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['nombre', 'capacidad'], context)
    if error:
        return None, error

    try:
        if item.get("id") is not None:
            validate_id_parameter(item["id"], "ID")

        name = validate_required_string(item["nombre"], "nombre")
        capacity = validate_integer(item["capacidad"], "capacidad", min_val=1)

        return {
            "id": item.get("id"),
            "name": name,
            "capacity": capacity
        }, None
    except FormValidationError as e:
        return None, standard_error(context, str(e))

def process_classroom_entry(valid_data, force):
    existing = Classroom.query.filter_by(name=valid_data["name"]).first()

    if existing and not force:
        return None, format_duplicate(existing.__dict__, valid_data, ['id', 'name', 'capacity'])

    if existing and force:
        existing.capacity = valid_data["capacity"]
        return 'updated', None

    classroom = Classroom(
        id=valid_data["id"],
        name=valid_data["name"],
        capacity=valid_data["capacity"]
    )
    db.session.add(classroom)
    return 'inserted', None

def import_classrooms(data, force=False):
    classrooms, structure_errors = validate_classrooms_data(data)
    if structure_errors:
        return standard_return(errors=structure_errors)

    inserted = 0
    updated = 0
    duplicated = []
    errors = []

    for item in classrooms:
        valid_data, error = validate_classroom(item)
        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        result, duplicate_info = process_classroom_entry(valid_data, force)

        if result == 'inserted':
            inserted += 1
        elif result == 'updated':
            inserted += 1
        elif duplicate_info:
            duplicated.append(duplicate_info)

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
