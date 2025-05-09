from models import db, Teacher

def validate_teacher(item):
    teacher_id = item.get("id")
    name = item.get("nombre")
    email = item.get("correo")

    if not name or not email:
        return None, f"ID {teacher_id or 'N/A'}: Missing required fields."

    if '@' not in email:
        return None, f"ID {teacher_id or 'N/A'}: Invalid email address: {email}"

    return {"id": teacher_id, "name": name, "email": email}, None

def format_teacher_duplicate(existing, item):
    return {
        "ya_existe": {
            "id": existing.id,
            "nombre": existing.name,
            "correo": existing.email
        },
        "nuevo": {
            "id": item.get("id"),
            "nombre": item.get("nombre"),
            "correo": item.get("correo")
        }
    }

def import_teachers(data, force=False):
    teachers = data.get("profesores", [])
    inserted = 0
    duplicated = []
    mistakes = []

    for item in teachers:
        valid_data, error = validate_teacher(item)
        if error:
            mistakes.append(error)
            continue

        email = valid_data["email"]
        existing = Teacher.query.filter_by(email=email).first()

        if existing and not force:
            duplicated.append(format_teacher_duplicate(existing, item))
            continue

        if existing and force:
            db.session.delete(existing)
            db.session.flush()

        teacher = Teacher(name=valid_data["name"], email=email)
        db.session.add(teacher)
        inserted += 1

    db.session.commit()

    return {
        "inserted": inserted,
        "ignored": len(mistakes), 
        "duplicated": duplicated,
        "mistakes": mistakes
    }
