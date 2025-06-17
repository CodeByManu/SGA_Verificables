from models import db, Course, Prerequisite
from utils.utils import (
    validate_required_fields,
    format_duplicate,
    safe_commit,
    standard_return,
    standard_error
)
from utils.types_validators import (
    validate_required_string,
    validate_course_code,
    validate_id_parameter,
    validate_integer,
    FormValidationError
)

def validate_courses_data(data):
    if not isinstance(data, dict):
        return None, ["El archivo debe ser un objeto JSON"]

    courses = data.get("cursos")
    if not isinstance(courses, list):
        return None, ["El campo 'cursos' debe ser una lista de objetos"]

    return courses, None

def process_course_entry(item, force):
    context = f"ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['codigo', 'descripcion'], context)
    if error:
        return None, None, None, error

    try:
        course_id = item.get("id")
        if course_id is not None:
            validate_id_parameter(course_id, "ID")

        code = validate_course_code(item["codigo"], "Código de curso")
        name = validate_required_string(item["descripcion"], "Descripción")
        description = name 
        credits = None

        if item.get("creditos") is not None:
            credits = validate_integer(item["creditos"], "Créditos", min_val=1, max_val=50)

        existing = Course.query.filter_by(code=code).first()

        if existing and not force:
            return None, format_duplicate(existing.__dict__, item, ['id', 'code', 'name', 'description', 'credits']), None

        if existing and force:
            existing.code = code
            existing.name = name
            existing.description = description
            existing.credits = credits
            return 'updated', None, item.get("requisitos", []), None

        course = Course(
            id=course_id,
            code=code,
            name=name,
            description=description,
            credits=credits
        )
        db.session.add(course)
        return 'inserted', None, item.get("requisitos", []), None

    except FormValidationError as e:
        return None, None, None, standard_error(context, str(e))

def create_prerequisite_relations(pending_list):
    for main_code, req_codes in pending_list:
        main_course = Course.query.filter_by(code=main_code).first()
        if not main_course:
            print(f"❌ Curso principal con código '{main_code}' no existe.")
            continue

        for req_code in req_codes:
            required_course = Course.query.filter_by(code=req_code).first()

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
    courses, structure_errors = validate_courses_data(data)
    if structure_errors:
        return standard_return(errors=structure_errors)

    inserted = 0
    updated = 0
    duplicated = []
    errors = []
    prereq_pending = []

    for item in courses:
        result, duplicate_info, prereqs, error = process_course_entry(item, force)

        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        if duplicate_info:
            duplicated.append(duplicate_info)
            continue

        if result == 'inserted':
            inserted += 1
        elif result == 'updated':
            updated += 1

        if prereqs:
            prereq_pending.append((item["codigo"], prereqs))

    db.session.commit()
    create_prerequisite_relations(prereq_pending)
    safe_commit()

    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
