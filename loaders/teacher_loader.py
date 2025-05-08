from models import db, Teacher

def import_teachers(data, force=False):
    profesores = data.get("profesores", [])
    inserted = 0
    ignored = 0
    duplicated = []

    for item in profesores:
        teacher_id = item.get('id')
        name = item.get('nombre')
        email = item.get('correo')

        if not name or not email:
            ignored += 1
            continue

        existing = Teacher.query.filter_by(email=email).first()
        if existing and not force:
            duplicated.append({
                "ya_existe": {
                    "id": existing.id,
                    "nombre": existing.name,
                    "correo": existing.email
                },
                "nuevo": {
                    "id": teacher_id,
                    "nombre": name,
                    "correo": email
                }
            })
            continue

        if existing and force:
            db.session.delete(existing)
            db.session.flush()

        teacher = Teacher(name=name, email=email)
        db.session.add(teacher)
        inserted += 1

    db.session.commit()
    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated
    }
