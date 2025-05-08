from models import db, Course, Prerequisite

def import_courses(data, force=False):
    cursos = data.get("cursos", [])
    inserted = 0
    ignored = 0
    prereq_pending = []
    duplicados = []

    for item in cursos:
        course_id = item.get("id")
        code = item.get("codigo")
        name = item.get("descripcion")

        if not course_id or not code or not name:
            ignored += 1
            continue

        existing = Course.query.get(course_id)
        if existing and not force:
            duplicados.append({
                "ya_existe": {
                    "id": existing.id,
                    "codigo": existing.code,
                    "nombre": existing.name,
                    "descripcion": existing.description
                },
                "nuevo": {
                    "id": course_id,
                    "codigo": code,
                    "nombre": name,
                    "descripcion": name  # O el campo correspondiente si difiere
                }
            })
            continue

        if existing and force:
            db.session.delete(existing)
            db.session.flush()

        course = Course(
            id=course_id,
            code=code,
            name=name,
            description=name
        )
        db.session.add(course)
        inserted += 1
        prereq_pending.append((code, item.get("requisitos", [])))

    db.session.commit()

    for main_code, requisitos in prereq_pending:
        main_course = Course.query.filter_by(code=main_code).first()
        for req_code in requisitos:
            required_course = Course.query.filter_by(code=req_code).first()
            if main_course and required_course:
                if not Prerequisite.query.filter_by(
                    main_course_id=main_course.id, 
                    required_course_id=required_course.id
                ).first():
                    db.session.add(Prerequisite(
                        main_course_id=main_course.id,
                        required_course_id=required_course.id
                    ))

    db.session.commit()

    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicados
    }
