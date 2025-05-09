from models import db, Course, Prerequisite

def validate_course(item):
    course_id = item.get("id")
    code = item.get("codigo")
    name = item.get("descripcion")
    credits = item.get("creditos")

    if not code or not name:
        return None, f"ID {course_id or 'N/A'}: Faltan campos obligatorios ('codigo' o 'descripcion')."

    course = Course(
        id=course_id,
        code=code,
        name=name,
        description=name,
        credits=credits
    )
    return course, None

def handle_course_duplicates(existing, item):
    return {
        "ya_existe": {
            "id": existing.id,
            "codigo": existing.code,
            "nombre": existing.name,
            "descripcion": existing.description,
            "creditos": existing.credits
        },
        "nuevo": {
            "id": item.get("id"),
            "codigo": item.get("codigo"),
            "nombre": item.get("descripcion"),
            "descripcion": item.get("descripcion"),
            "creditos": item.get("creditos")
        }
    }

def create_prerequisite_relations(pending_list):
    for main_code, req_codes in pending_list:
        main_course = Course.query.filter_by(code=main_code).first()
        for req_code in req_codes:
            required_course = Course.query.filter_by(code=req_code).first()

            if not main_course:
                print(f"❌ Curso principal con código '{main_code}' no existe.")
                break

            if not required_course:
                print(f"⚠️ Curso requerido con código '{req_code}' no existe. No se creará la relación.")
                continue

            exists = Prerequisite.query.filter_by(
                main_course_id=main_course.id,
                required_course_id=required_course.id
            ).first()
            if not exists:
                db.session.add(Prerequisite(
                    main_course_id=main_course.id,
                    required_course_id=required_course.id
                ))

    db.session.commit()

def import_courses(data, force=False):
    courses = data.get("cursos", [])
    inserted = 0
    duplicated = []
    mistakes = []
    prereq_pending = []

    for item in courses:
        code = item.get("codigo")
        requisitos = item.get("requisitos", [])

        course, error = validate_course(item)
        if error:
            print(f"⚠️ {error}")
            mistakes.append(error)
            continue

        existing = Course.query.filter_by(code=code).first()
        if existing and not force:
            duplicated.append(handle_course_duplicates(existing, item))
            continue

        if existing and force:
            db.session.delete(existing)
            db.session.flush()

        db.session.add(course)
        inserted += 1
        prereq_pending.append((code, requisitos))

    db.session.commit()
    create_prerequisite_relations(prereq_pending)

    return {
        "inserted": inserted,
        "ignored": len(mistakes),
        "duplicated": duplicated,
        "mistakes": mistakes
    }
