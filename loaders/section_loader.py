from models import db, Section, Teacher, Evaluation, Task, Period
from datetime import date
from utils.utils import (
    validate_required_fields,
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return
)
from utils.types_validators import (
    validate_id_parameter,
    FormValidationError
)

def validate_sections_data(data):
    if not isinstance(data, dict):
        return None, ["El archivo debe ser un objeto JSON"]

    sections = data.get("secciones")
    if not isinstance(sections, list):
        return None, ["El campo 'secciones' debe ser una lista de objetos"]

    return sections, None

def validate_section_entry(entry):
    if not isinstance(entry, dict):
        return None, "Entrada no válida: no es un diccionario"

    context = f"Sección ID {entry.get('id') or 'N/A'}"
    valid_data, error = validate_required_fields(entry, ['id', 'instancia_curso', 'profesor_id', 'evaluacion'], context)
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

def create_evaluation_and_tasks(section_id, topic_combination, topic_info, force=False):
    existing_eval = Evaluation.query.filter_by(
        section_id=section_id,
        name=topic_combination.get("nombre")
    ).first()

    if existing_eval and force:
        for task in existing_eval.tasks:
            db.session.delete(task)
        existing_eval.tasks_weight_type = topic_info["tipo"]
        existing_eval.weight = topic_combination.get("valor", 1.0)
        db.session.flush()
        evaluation = existing_eval
    else:
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

def validate_section_references(section_input):
    teacher = Teacher.query.get(section_input["teacher_id"])
    if not teacher:
        return None, standard_error(f"profesor_id={section_input['teacher_id']}", "no existe.")

    period = Period.query.get(section_input["period_id"])
    if not period:
        return None, standard_error(f"periodo_id={section_input['period_id']}", "no existe.")

    return {"teacher": teacher, "period": period}, None

def upsert_section(section_input, force):
    section_id = section_input["id"]
    existing = Section.query.get(section_id)

    if existing and not force:
        return None, format_duplicate(existing.__dict__, section_input, ["id", "period_id", "teacher_id"]), None

    if existing and force:
        existing.period_id = section_input["period_id"]
        existing.teacher_id = section_input["teacher_id"]
        existing.section_number = section_input["number"] or str(section_id)
        existing.evaluation_weight_type = section_input["evaluation_weight_type"]
        for evaluation in existing.evaluations:
            for task in evaluation.tasks:
                db.session.delete(task)
            db.session.delete(evaluation)
        db.session.flush()
        return existing, None, None

    section = Section(
        id=section_id,
        period_id=section_input["period_id"],
        teacher_id=section_input["teacher_id"],
        section_number=section_input["number"] or str(section_id),
        evaluation_weight_type=section_input["evaluation_weight_type"]
    )
    db.session.add(section)
    db.session.flush()
    return section, None, None

def apply_evaluation_structure(section, section_input, force):
    for comb in section_input["topic_combinations"]:
        topic_id = str(comb.get("id"))
        topic_info = section_input["topics"].get(topic_id)
        create_evaluation_and_tasks(section.id, comb, topic_info, force=force)

def process_section_entry(entry, force):
    section_input, error = validate_section_entry(entry)
    if error:
        return None, None, error

    try:
        validate_id_parameter(section_input["id"], "ID sección")
        validate_id_parameter(section_input["teacher_id"], "ID profesor")
        validate_id_parameter(section_input["period_id"], "ID período")

        references, ref_error = validate_section_references(section_input)
        if ref_error:
            return None, None, ref_error

        comb_error = validate_topic_combinations(section_input["topic_combinations"], section_input["evaluation_weight_type"])
        if comb_error:
            return None, None, standard_error(f"seccion_id={section_input['id']}", f"combinación inválida: {comb_error}")

        topics_error = validate_topics(section_input["topics"], section_input["topic_combinations"])
        if topics_error:
            return None, None, standard_error(f"seccion_id={section_input['id']}", f"tópicos inválidos: {topics_error}")

        section, duplicate_info, err = upsert_section(section_input, force)
        if err or duplicate_info:
            return None, duplicate_info, err

        apply_evaluation_structure(section, section_input, force)

        return 'inserted', None, None

    except FormValidationError as e:
        return None, None, standard_error(f"seccion_id={entry.get('id')}", str(e))

def import_sections_with_evaluations(data, force=False):
    sections_data, structure_errors = validate_sections_data(data)
    if structure_errors:
        return {
            "sections_inserted": 0,
            "ignored": 0,
            "duplicated": [],
            "errors": structure_errors
        }

    inserted = 0
    duplicated = []
    errors = []

    for entry in sections_data:
        result, duplicate_info, error = process_section_entry(entry, force)

        if error:
            print(f"⚠️ Sección ignorada: {error}")
            errors.append(error)
            continue

        if duplicate_info:
            duplicated.append(duplicate_info)
            continue

        if result == 'inserted':
            inserted += 1

    safe_commit()
    result = standard_return(inserted=inserted, ignored=len(errors), duplicated=duplicated, errors=errors)
    result["sections_inserted"] = result.pop("inserted")
    return result
