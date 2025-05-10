from models import db, Teacher
from utils.utils import (
    is_valid_email,
    standard_error,
    validate_required_fields,
    format_duplicate,
    safe_commit,
    standard_return
)

def validate_teacher(item):
    context = f"ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['nombre', 'correo'], context)
    if error:
        return None, error

    email = item.get("correo")
    if not is_valid_email(email):
        return None, standard_error(context, f"Correo inválido: {email}")

    return {
        "id": item.get("id"),
        "name": item["nombre"],
        "email": email
    }, None

def import_teachers(data, force=False):
    teachers = data.get("profesores", [])
    inserted = 0
    duplicated = []
    errors = []

    for item in teachers:
        valid_data, error = validate_teacher(item)
        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        existing = Teacher.query.filter_by(email=valid_data["email"]).first()

        if existing and not force:
            duplicated.append(format_duplicate(existing.__dict__, item, ['id', 'name', 'email']))
            continue

        if existing and force:
            existing.name = valid_data["name"]
            existing.email = valid_data["email"]
            inserted += 1  
            continue

        teacher = Teacher(
            id=valid_data["id"],
            name=valid_data["name"],
            email=valid_data["email"]
        )
        db.session.add(teacher)
        inserted += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
