from models import db, Classroom
from utils.utils import (
    validate_required_fields,
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return
)

def validate_classroom(item):
    context = f"Sala ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['nombre', 'capacidad'], context)
    if error:
        return None, error

    try:
        capacidad = int(item['capacidad'])
        if capacidad <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return None, standard_error(context, f"Capacidad inválida: {item['capacidad']}")

    return {
        "id": item.get("id"),
        "name": item["nombre"],
        "capacity": capacidad
    }, None

def import_classrooms(data, force=False):
    classrooms = data.get("salas", [])
    inserted = 0
    duplicated = []
    errors = []

    for item in classrooms:
        valid_data, error = validate_classroom(item)
        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        existing = Classroom.query.filter_by(name=valid_data["name"]).first()

        if existing and not force:
            duplicated.append(format_duplicate(existing.__dict__, item, ['id', 'name', 'capacity']))
            continue

        if existing and force:
            existing.capacity = valid_data["capacity"]
            inserted += 1
            continue

        classroom = Classroom(
            id=valid_data["id"],
            name=valid_data["name"],
            capacity=valid_data["capacity"]
        )
        db.session.add(classroom)
        inserted += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
