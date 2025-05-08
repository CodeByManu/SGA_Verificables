from models import db, Period

def import_periods(data, force=False):
    año = data.get("año")
    semestre = data.get("semestre")
    instancias = data.get("instancias", [])

    inserted = 0
    ignored = 0
    duplicated = []
    print(f"📅 Procesando instancias para {año}-{semestre}")
    print(f"Instancias encontradas: {len(instancias)}")

    for item in instancias:

        course_id = item.get("curso_id")
        period_id = item.get("id")
        period_name = f"{año}-{semestre}"
        print(f"→ Candidato: id={period_id}, course_id={course_id}")
        
        if not course_id or not period_id:
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
