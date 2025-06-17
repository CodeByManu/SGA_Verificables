from models import db, Course, Period
from utils.utils import (
    validate_required_fields,
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return
)
from utils.types_validators import (
    validate_id_parameter,
    validate_integer,
    FormValidationError
)

def validate_periods_data(data):
    if not isinstance(data, dict):
        return None, None, None, ["El archivo debe ser un objeto JSON"]

    instancias = data.get("instancias")
    if not isinstance(instancias, list):
        return None, None, None, ["El campo 'instancias' debe ser una lista de objetos"]

    try:
        año = validate_integer(data.get("año"), "Año", min_val=2000, max_val=2100)
        semestre = validate_integer(data.get("semestre"), "Semestre", min_val=1, max_val=2)
    except FormValidationError as e:
        return None, None, None, [f"Error en metadatos del período: {str(e)}"]

    return instancias, año, semestre, None


def process_period_entry(item, año, semestre, force):
    context = f"Periodo ID {item.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(item, ['id', 'curso_id'], context)
    if error:
        return None, None, error

    try:
        period_id = validate_id_parameter(item["id"], "ID")
        course_id = validate_id_parameter(item["curso_id"], "ID de curso")

        course = Course.query.get(course_id)
        if not course:
            return None, None, standard_error(context, f"course_id {course_id} no existe")

        period_name = f"{año}-{semestre}"
        existing = Period.query.get(period_id)

        if existing and not force:
            return None, format_duplicate(existing.__dict__, item, ['id', 'course_id', 'period']), None

        if existing and force:
            existing.course_id = course_id
            existing.period = period_name
            return 'updated', None, None

        period = Period(
            id=period_id,
            course_id=course_id,
            period=period_name
        )
        db.session.add(period)
        return 'inserted', None, None

    except FormValidationError as e:
        return None, None, standard_error(context, str(e))


def import_course_periods(data, force=False):
    instancias, año, semestre, structure_errors = validate_periods_data(data)
    if structure_errors:
        return standard_return(errors=structure_errors)

    inserted = 0
    updated = 0
    duplicated = []
    errors = []

    for item in instancias:
        result, duplicate_info, error = process_period_entry(item, año, semestre, force)

        if error:
            print(f"⚠️ Ignorado: {error}")
            errors.append(error)
            continue

        if duplicate_info:
            duplicated.append(duplicate_info)
            continue

        if result == 'inserted':
            inserted += 1
        elif result == 'updated':
            updated += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
