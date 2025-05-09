from models import db, Course, Period

def validate_period_instance(item, año, semestre):
    period_id = item.get("id")
    course_id = item.get("curso_id")
    period_name = f"{año}-{semestre}"

    if not period_id or not course_id:
        return None, None, "Faltan datos obligatorios"

    course = Course.query.get(course_id)
    if not course:
        return None, None, f"course_id {course_id} no existe"

    return period_id, course_id, None  # no error

def format_period_duplicate(existing, item, period_name):
    return {
        "ya_existe": {
            "id": existing.id,
            "course_id": existing.course_id,
            "period": existing.period
        },
        "nuevo": {
            "id": item.get("id"),
            "course_id": item.get("curso_id"),
            "period": period_name
        }
    }

def import_course_periods(data, force=False):
    año = data.get("año")
    semestre = data.get("semestre")
    instancias = data.get("instancias", [])

    inserted = 0
    ignored = 0
    duplicated = []

    for item in instancias:
        period_id = item.get("id")
        course_id = item.get("curso_id")
        period_name = f"{año}-{semestre}"

        period_id, course_id, error = validate_period_instance(item, año, semestre)
        if error:
            print(f"⚠️ Ignorado: {error}")
            ignored += 1
            continue

        existing = Period.query.get(period_id)

        if existing and not force:
            duplicated.append(format_period_duplicate(existing, item, period_name))
            continue

        if existing and force:
            db.session.delete(existing)
            db.session.flush()

        p = Period(id=period_id, course_id=course_id, period=period_name)
        db.session.add(p)
        inserted += 1

    db.session.commit()

    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated
    }
