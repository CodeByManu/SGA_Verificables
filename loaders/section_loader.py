from models import db, Section, Teacher, Evaluation, Task, Period
from datetime import date
from utils.utils import (
    validate_required_fields,
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return
)

def validate_section_entry(entry):
    if not isinstance(entry, dict):
        return None, "Entrada no válida: no es un diccionario"

    context = f"Sección ID {entry.get('id') or 'N/A'}"
    required, error = validate_required_fields(entry, ['id', 'instancia_curso', 'profesor_id', 'evaluacion'], context)
    if error:
        return None, error

    return {
        "id": entry["id"],
        "period_id": entry["instancia_curso"],
        "teacher_id": entry["profesor_id"],
        "number": entry.get("numero"),
        "evaluation_data": entry["evaluacion"],
        "topics": entry["evaluacion"].get("topicos"),
        "topic_combinations": entry["evaluacion"].get("combinacion_topicos", []),
        "evaluation_weight_type": entry["evaluacion"].get("tipo", "desconocido")
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
        for field in ["tipo", "cantidad"]:
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

def create_task(evaluation_id, topic_id, nombre, valores, obligatorias):
    for i in range(len(valores)):
        task_name = f"{nombre or f'Tópico {topic_id}'} #{i+1}"
        task = Task(
            evaluation_id=evaluation_id,
            name=task_name,
            date=date.today(),
            weight=valores[i],
            is_optional=not obligatorias[i]
        )
        db.session.add(task)

def create_evaluation_and_tasks(section_id, topic_combination, topic_info):
    evaluation = Evaluation(
        name=topic_combination.get("nombre", f"Evaluación {topic_combination['id']}"),
        section_id=section_id,
        tasks_weight_type=topic_info["tipo"],
        weight=topic_combination.get("valor", 1.0)
    )
    db.session.add(evaluation)
    db.session.flush()

    create_task(
        evaluation.id,
        topic_combination["id"],
        topic_combination.get("nombre"),
        topic_info["valores"],
        topic_info["obligatorias"]
    )

def import_sections_with_evaluations(data, force=False):
    sections_data = data.get("secciones", [])
    inserted = 0
    duplicated = []
    errors = []

    if not isinstance(sections_data, list):
        return {
            "sections_inserted": 0,
            "ignored": 0,
            "duplicated": [],
            "errors": ["El campo 'secciones' no es una lista"]
        }

    for entry in sections_data:
        section_input, error = validate_section_entry(entry)
        if error:
            print(f"⚠️ Sección ignorada: {error}")
            errors.append(error)
            continue

        teacher = Teacher.query.get(section_input["teacher_id"])
        period = Period.query.get(section_input["period_id"])

        if not teacher:
            msg = f"❌ Profesor con id={section_input['teacher_id']} no existe."
            print(msg)
            errors.append(msg)
            continue

        if not period:
            msg = f"❌ Periodo con id={section_input['period_id']} no existe."
            print(msg)
            errors.append(msg)
            continue

        comb_error = validate_topic_combinations(section_input["topic_combinations"], section_input["evaluation_weight_type"])
        if comb_error:
            msg = f"❌ Combinación inválida: {comb_error}"
            print(msg)
            errors.append(msg)
            continue

        topics_error = validate_topics(section_input["topics"], section_input["topic_combinations"])
        if topics_error:
            msg = f"❌ Tópicos inválidos: {topics_error}"
            print(msg)
            errors.append(msg)
            continue

        existing = Section.query.get(section_input["id"])
        if existing and not force:
            duplicated.append(format_duplicate(existing.__dict__, section_input, ["id", "period_id", "teacher_id"]))
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
            create_evaluation_and_tasks(section.id, comb, topic_info)

        inserted += 1

    safe_commit()
    result = standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
    result["sections_inserted"] = result.pop("inserted")
    return result


