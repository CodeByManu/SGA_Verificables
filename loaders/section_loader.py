from models import db, Section, Teacher, Evaluation, Task, Period
from datetime import date

def validate_section_entry(entry):
    if not isinstance(entry, dict):
        return None, "Entrada no válida: no es un diccionario"

    section_id = entry.get("id")
    period_id = entry.get("instancia_curso")
    teacher_id = entry.get("profesor_id")
    evaluation_data = entry.get("evaluacion")

    if not section_id or not period_id or not teacher_id or not evaluation_data:
        return None, "Faltan campos obligatorios en la sección"

    return {
        "id": section_id,
        "period_id": period_id,
        "teacher_id": teacher_id,
        "number": entry.get("numero"),
        "evaluation_data": evaluation_data,
        "topics": evaluation_data.get("topicos"),
        "topic_combinations": evaluation_data.get("combinacion_topicos", []),
        "evaluation_weight_type": evaluation_data.get("tipo", "desconocido")
    }, None

def validate_topic_combinations(combinations, weight_type):
    if not combinations:
        return "No se definieron combinaciones de tópicos."

    if weight_type == "porcentaje":
        total = sum(comb.get("valor", 0) for comb in combinations)
        if abs(total - 100.0) > 0.1:
            return f"La suma de porcentajes debe ser 100. Actualmente: {total}"

    for comb in combinations:
        if not comb.get("id") or "valor" not in comb:
            return f"Combinación inválida: falta 'id' o 'valor'."

    return None

def validate_topics(topics, combinations):
    if not topics:
        return "No se definieron los tópicos."

    for comb in combinations:
        topic_id = str(comb.get("id"))
        if topic_id not in topics:
            return f"El tópico '{topic_id}' no tiene definición."

        topic_info = topics[topic_id]
        required_fields = ["tipo", "cantidad"]

        for field in required_fields:
            if field not in topic_info:
                return f"El tópico '{topic_id}' no tiene el campo obligatorio '{field}'."

        cantidad = topic_info["cantidad"]
        valores = topic_info.get("valores", [])
        obligatorias = topic_info.get("obligatorias", [])

        if len(valores) != cantidad:
            return f"Tópico '{topic_id}' tiene {cantidad} ítems, pero {len(valores)} valores."

        if len(obligatorias) != cantidad:
            return f"Tópico '{topic_id}' tiene {cantidad} ítems, pero {len(obligatorias)} campos 'obligatorias'."

    return None

def format_section_duplicate(existing, section_input):
    return {
        "ya_existe": {
            "id": existing.id,
            "period_id": existing.period_id,
            "teacher_id": existing.teacher_id
        },
        "nuevo": {
            "id": section_input["id"],
            "period_id": section_input["period_id"],
            "teacher_id": section_input["teacher_id"]
        }
    }

def import_sections_with_evaluations(data, force=False):
    sections_data = data.get("secciones", [])
    inserted = 0
    ignored = 0
    duplicated = []

    if not isinstance(sections_data, list):
        return {
            "sections_inserted": 0,
            "ignored": 0,
            "duplicated": [],
            "error": "El campo 'secciones' no es una lista"
        }

    for entry in sections_data:
        section_input, error = validate_section_entry(entry)
        if error:
            print(f"⚠️ Sección ignorada: {error}")
            ignored += 1
            continue

        teacher = Teacher.query.get(section_input["teacher_id"])
        period = Period.query.get(section_input["period_id"])

        if not teacher:
            print(f"❌ Profesor con id={section_input['teacher_id']} no existe.")
            ignored += 1
            continue

        if not period:
            print(f"❌ Periodo con id={section_input['period_id']} no existe.")
            ignored += 1
            continue

        comb_error = validate_topic_combinations(section_input["topic_combinations"], section_input["evaluation_weight_type"])
        if comb_error:
            print(f"❌ Combinación inválida: {comb_error}")
            ignored += 1
            continue

        topics_error = validate_topics(section_input["topics"], section_input["topic_combinations"])
        if topics_error:
            print(f"❌ Tópicos inválidos: {topics_error}")
            ignored += 1
            continue

        existing = Section.query.get(section_input["id"])
        if existing and not force:
            duplicated.append(format_section_duplicate(existing, section_input))
            continue
        elif existing and force:
            for evaluation in existing.evaluations:
                for task in evaluation.tasks:
                    db.session.delete(task)
                db.session.delete(evaluation)
            db.session.delete(existing)
            db.session.flush()

        section = Section(
            id=section_input["id"],
            period_id=section_input["period_id"],
            teacher_id=section_input["teacher_id"],
            section_number=section_input["number"] or str(section_input["id"]),
            evaluation_weight_type=section_input["evaluation_weight_type"]
        )
        db.session.add(section)
        db.session.flush()

        for comb in section_input["topic_combinations"]:
            topic_id = str(comb.get("id"))
            topic_info = section_input["topics"].get(topic_id)

            evaluation = Evaluation(
                name=comb.get("nombre", f"Evaluación {topic_id}"),
                section_id=section.id,
                tasks_weight_type=topic_info["tipo"],
                weight=comb.get("valor", 1.0)
            )
            db.session.add(evaluation)
            db.session.flush()

            for i in range(topic_info["cantidad"]):
                task_name = f"{comb.get('nombre', f'Tópico {topic_id}')} #{i+1}"
                task_weight = topic_info["valores"][i]
                is_optional = not topic_info["obligatorias"][i]

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
