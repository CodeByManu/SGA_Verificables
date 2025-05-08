from models import db, Student

def import_students(data, force=False):
    alumnos = data.get('alumnos', [])
    inserted = 0
    ignored = 0
    duplicated = []

    for item in alumnos:
        student_id = item.get('id')
        name = item.get('nombre')
        email = item.get('correo')
        admission_date = item.get('anio_ingreso')

        if not name or not email or not admission_date:
            ignored += 1
            continue

        existing = Student.query.filter_by(email=email).first()
        if existing and not force:
            duplicated.append({
                "ya_existe": {
                    "id": existing.id,
                    "nombre": existing.name,
                    "correo": existing.email,
                    "anio_ingreso": existing.admission_date
                },
                "nuevo": {
                    "id": student_id,
                    "nombre": name,
                    "correo": email,
                    "anio_ingreso": admission_date
                }
            })
            continue

        if existing and force:
            db.session.delete(existing)
            db.session.flush()

        student = Student(name=name, email=email, admission_date=admission_date)
        db.session.add(student)
        inserted += 1

    db.session.commit()
    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated
    }
