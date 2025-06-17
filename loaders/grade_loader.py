from models import db, Grade, Task, Student, Evaluation, StudentSection
from utils.utils import (
    validate_required_fields,
    standard_error,
    safe_commit,
    standard_return
)
from utils.types_validators import (
    validate_id_parameter,
    validate_integer,
    validate_float,
    FormValidationError
)

def validate_grades_data(data):
    if not isinstance(data, dict):
        return None, ["El archivo debe ser un objeto JSON"]

    grades = data.get("notas")
    if not isinstance(grades, list):
        return None, ["El campo 'notas' debe ser una lista de objetos"]

    return grades, None

def validate_grade_entry(entry):
    context = f"alumno_id={entry.get('alumno_id', 'N/A')}, topico_id={entry.get('topico_id', 'N/A')}, instancia={entry.get('instancia', 'N/A')}"
    validated, error = validate_required_fields(entry, ['alumno_id', 'topico_id', 'instancia'], context)
    if error:
        return None, error

    try:
        student_id = validate_id_parameter(entry['alumno_id'], "alumno_id")
        evaluation_id = validate_id_parameter(entry['topico_id'], "topico_id")
        instance = validate_integer(entry['instancia'], "instancia", min_val=1)
        value = validate_float(entry['nota'], "nota", min_val=1.0, max_val=7.0, decimal_places=1)
        return {
            "student_id": student_id,
            "evaluation_id": evaluation_id,
            "instance": instance,
            "value": value
        }, None

    except FormValidationError as e:
        return None, standard_error(context, str(e))

def format_grade_duplicate(existing, new_value):
    return {
        "ya_existe": {
            "student_id": existing.student_id,
            "task_id": existing.task_id,
            "nota": existing.value
        },
        "nuevo": {
            "student_id": existing.student_id,
            "task_id": existing.task_id,
            "nota": new_value
        }
    }

def process_grade_entry(validated, force, seen):
    key = (validated["student_id"], validated["evaluation_id"], validated["instance"])
    if key in seen:
        return None, standard_error(
            f"(alumno_id={key[0]}, topico_id={key[1]}, instancia={key[2]}, nota={validated['value']})",
            f"Dato repetido en archivo. Ya existe con nota={seen[key]}"
        )

    seen[key] = validated["value"]

    student = Student.query.get(validated["student_id"])
    if not student:
        return None, standard_error(f"alumno_id={validated['student_id']}", "no existe.")

    evaluation = Evaluation.query.get(validated["evaluation_id"])
    if not evaluation:
        return None, standard_error(f"topico_id={validated['evaluation_id']}", "no existe.")

    student_sections = StudentSection.query.filter_by(student_id=student.id).all()
    section_ids = [s.section_id for s in student_sections]
    if evaluation.section_id not in section_ids:
        return None, standard_error(
            f"alumno_id={student.id}, topico_id={evaluation.id}",
            f"pertenece a sección {evaluation.section_id}, no a las del alumno: {section_ids}"
        )

    tasks = Task.query.filter_by(evaluation_id=evaluation.id).order_by(Task.id).all()
    if len(tasks) < validated["instance"]:
        return None, standard_error(f"instancia={validated['instance']}", f"solo hay {len(tasks)} tareas.")

    task = tasks[validated["instance"] - 1]
    existing = Grade.query.filter_by(student_id=student.id, task_id=task.id).first()

    if existing:
        if existing.value == validated["value"]:
            return 'skipped', None
        if not force:
            return 'duplicated', format_grade_duplicate(existing, validated["value"])
        else:
            existing.value = validated["value"]
            return 'updated', None

    db.session.add(Grade(
        student_id=student.id,
        task_id=task.id,
        value=validated["value"]
    ))
    return 'inserted', None

def import_grades(data, force=False):
    raw_grades, structure_errors = validate_grades_data(data)
    if structure_errors:
        return standard_return(errors=structure_errors)

    inserted = 0
    ignored = 0
    duplicated = []
    errors = []
    seen = {}

    for entry in raw_grades:
        validated, error = validate_grade_entry(entry)
        if error:
            print(f"⚠️ {error}")
            errors.append(error)
            ignored += 1
            continue

        result, info = process_grade_entry(validated, force, seen)

        if result == 'inserted':
            inserted += 1
        elif result == 'duplicated':
            duplicated.append(info)
        elif result == 'skipped':
            continue
        elif result == 'updated':
            inserted += 1
        elif info:
            errors.append(info)
            ignored += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=ignored, duplicated=duplicated, errors=errors)
