from models import db, Section, Teacher, Evaluation, Task
from datetime import date

def import_sections_with_evaluations(data, force=False):
    inserted = 0
    ignored = 0
    duplicated = []

    secciones = data.get("secciones", [])
    if not isinstance(secciones, list):
        return {
            "sections_inserted": 0,
            "ignored": 0,
            "duplicated": [],
            "error": "El campo 'secciones' no es una lista"
        }

    for entry in secciones:
        if not isinstance(entry, dict):
            ignored += 1
            continue

        section_id = entry.get("id")
        period_id = entry.get("instancia_curso")
        number = entry.get("numero")
        teacher_id = entry.get("profesor_id")
        evaluacion = entry.get("evaluacion")
        topicos = evaluacion.get("topicos") if evaluacion else None

        if not section_id or not period_id or not teacher_id or not evaluacion:
            ignored += 1
            continue

        existing = Section.query.get(section_id)
        if existing:
            if not force:
                duplicated.append({
                    "ya_existe": {
                        "id": existing.id,
                        "period_id": existing.period_id,
                        "teacher_id": existing.teacher_id
                    },
                    "nuevo": {
                        "id": section_id,
                        "period_id": period_id,
                        "teacher_id": teacher_id
                    }
                })
                continue
            else:
                for eval in existing.evaluations:
                    for task in eval.tasks:
                        db.session.delete(task)
                    db.session.delete(eval)
                db.session.delete(existing)
                db.session.flush()

        section = Section(
            id=section_id,
            period_id=period_id,
            teacher_id=teacher_id,
            section_number=number or str(section_id),
            evaluation_weight_type=evaluacion.get("tipo", "desconocido")
        )
        db.session.add(section)
        db.session.flush()

        combinaciones = evaluacion.get("combinacion_topicos", [])

        for comb in combinaciones:
            topic_id = str(comb.get("id"))
            topic_info = topicos.get(topic_id) if topicos else None
            if not topic_info:
                continue

            evaluation = Evaluation(
                name=comb.get("nombre", f"Evaluacion {topic_id}"),
                section_id=section.id,
                tasks_weight_type=topic_info.get("tipo"),
                weight=comb.get("valor", 1.0)
            )
            db.session.add(evaluation)
            db.session.flush()

            cantidad = topic_info.get("cantidad", 0)
            valores = topic_info.get("valores", [])
            obligatorias = topic_info.get("obligatorias", [])

            for i in range(cantidad):
                task_name = f"{comb.get('nombre', f'Topico {topic_id}')} #{i+1}"
                task_weight = valores[i] if i < len(valores) else 0.0
                is_optional = not obligatorias[i] if i < len(obligatorias) else False

                task = Task(
                    evaluation_id=evaluation.id,
                    name=task_name,
                    date=date.today(),
                    weight=task_weight,
                    is_optional=is_optional
                )
                db.session.add(task)

        inserted += 1

    db.session.commit()
    return {
        "sections_inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated
    }
