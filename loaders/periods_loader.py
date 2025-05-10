from models import db, Course, Period
from utils.utils import (
    validate_required_fields,
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return
)

def validate_period_instance(item, año, semestre):
    context = f"Periodo ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['id', 'curso_id'], context)
    if error:
        return None, error

    course_id = item.get("curso_id")
    course = Course.query.get(course_id)
    if not course:
        return None, standard_error(context, f"course_id {course_id} no existe")

    return {
        "id": item["id"],
        "course_id": course_id,
        "period_name": f"{año}-{semestre}"
    }, None

def import_course_periods(data, force=False):
    año = data.get("año")
    semestre = data.get("semestre")
    instancias = data.get("instancias", [])

    inserted = 0
    duplicated = []
    errors = []

    for item in instancias:
        period_data, error = validate_period_instance(item, año, semestre)
        if error:
            print(f"⚠️ Ignorado: {error}")
            errors.append(error)
            continue

        existing = Period.query.get(period_data["id"])
        if existing and not force:
            duplicated.append(format_duplicate(existing.__dict__, item, ['id', 'course_id', 'period']))
            continue

        if existing and force:
            existing.course_id = period_data["course_id"]
            existing.period = period_data["period_name"]
            inserted += 1  # ✅ contar sobrescritura
            continue

        period = Period(
            id=period_data["id"],
            course_id=period_data["course_id"],
            period=period_data["period_name"]
        )
        db.session.add(period)
        inserted += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
