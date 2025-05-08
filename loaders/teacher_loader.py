from models import db, Teacher

def import_teachers(data):
    inserted = 0
    ignored = 0

    for entry in data.get("profesores", []):
        if not entry.get("nombre") or not entry.get("correo"):
            ignored += 1
            continue

        if Teacher.query.filter_by(email=entry["correo"]).first():
            ignored += 1
            continue

        teacher = Teacher(name=entry["nombre"], email=entry["correo"])
        db.session.add(teacher)
        inserted += 1

    db.session.commit()
    return inserted, ignored
