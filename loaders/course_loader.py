from models import db, Course, Prerequisite
from utils.utils import (
    validate_required_fields,
    format_duplicate,
    safe_commit,
    standard_return
)

def validate_course(item):
    context = f"ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['codigo', 'descripcion'], context)
    if error:
        return None, error

    course = Course(
        id=item.get("id"),
        code=item.get("codigo"),
        name=item.get("descripcion"),
        description=item.get("descripcion"),
        credits=item.get("creditos")
    )
    return course, None

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

def import_courses(data, force=False):
    courses = data.get("cursos", [])
    inserted = 0
    duplicated = []
    errors = []
    prereq_pending = []

    for item in courses:
        course, error = validate_course(item)
        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        code = item.get("codigo")
        requisitos = item.get("requisitos", [])

        existing = Course.query.filter_by(code=code).first()

        if existing and not force:
            duplicated.append(format_duplicate(existing.__dict__, item, ['id', 'code', 'name', 'description', 'credits']))
            continue

        if existing and force:
            existing.code = item["codigo"]
            existing.name = item["descripcion"]
            existing.description = item["descripcion"]
            existing.credits = item.get("creditos")
            inserted += 1  
            prereq_pending.append((code, requisitos))
            continue

        db.session.add(course)
        inserted += 1
        prereq_pending.append((code, requisitos))

    db.session.commit()
    create_prerequisite_relations(prereq_pending)

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
