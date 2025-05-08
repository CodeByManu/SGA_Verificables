from models import db, Course, Period

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

        if not period_id or not course_id:
            print(f"⚠️ Ignorado por falta de datos.")
            ignored += 1
            continue

        course = Course.query.get(course_id)
        if not course:
            print(f"❌ Ignorado: course_id {course_id} no existe.")
            ignored += 1
            continue

        existing = Period.query.get(period_id)

        if existing and not force:
            duplicated.append({
                "ya_existe": {
                    "id": existing.id,
                    "course_id": existing.course_id,
                    "period": existing.period
                },
                "nuevo": {
                    "id": period_id,
                    "course_id": course_id,
                    "period": period_name
                }
            })
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
