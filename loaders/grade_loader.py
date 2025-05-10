from models import db, Grade, Task, Student, Evaluation, StudentSection
from utils.utils import (
    validate_required_fields,
    standard_error,
    safe_commit,
    standard_return
)

def validate_grade_entry(entry):
    context = f"alumno_id={entry.get('alumno_id', 'N/A')}, topico_id={entry.get('topico_id', 'N/A')}, instancia={entry.get('instancia', 'N/A')}"
    validated, error = validate_required_fields(entry, ['alumno_id', 'topico_id', 'instancia'], context)
    if error:
        return None, error

    nota = entry.get("nota")
    if nota is None or nota == "":
        return None, standard_error(context, "Falta valor de nota.")
    try:
        nota = float(nota)
    except ValueError:
        return None, standard_error(context, f"Nota inválida: '{nota}' no es un número.")

    return {
        "student_id": entry["alumno_id"],
        "evaluation_id": entry["topico_id"],
        "instance": entry["instancia"],
        "value": nota
    }, None


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

def import_grades(data, force=False):
    raw_grades = data.get("notas", [])
    inserted = 0
    ignored = 0
    duplicated = []
    errors = []
    seen = {} 

    for entry in raw_grades:
        validated, error = validate_grade_entry(entry)
        if error:
            ignored += 1
            print(f"⚠️ {error}")
            errors.append(error)
            continue

        key = (validated["student_id"], validated["evaluation_id"], validated["instance"])
        if key in seen:
            nota_anterior = seen[key]
            msg = standard_error(
                f"(alumno_id={key[0]}, topico_id={key[1]}, instancia={key[2]}, nota={validated['value']})",
                f"Dato repetido en archivo. Ya existe con nota={nota_anterior}"
            )
            print(f"❌ {msg}")
            errors.append(msg)
            ignored += 1
            continue

        # Guardamos la nota para detección futura
        seen[key] = validated["value"]


        student = Student.query.get(validated["student_id"])
        if not student:
            msg = standard_error(f"alumno_id={validated['student_id']}", "no existe.")
            print(f"❌ {msg}")
            errors.append(msg)
            ignored += 1
            continue

        evaluation = Evaluation.query.get(validated["evaluation_id"])
        if not evaluation:
            msg = standard_error(f"topico_id={validated['evaluation_id']}", "no existe.")
            print(f"❌ {msg}")
            errors.append(msg)
            ignored += 1
            continue

        student_sections = StudentSection.query.filter_by(student_id=student.id).all()
        section_ids = [s.section_id for s in student_sections]
        if evaluation.section_id not in section_ids:
            msg = standard_error(
                f"alumno_id={student.id}, topico_id={evaluation.id}",
                f"pertenece a sección {evaluation.section_id}, no a las del alumno: {section_ids}"
            )
            print(f"❌ {msg}")
            errors.append(msg)
            ignored += 1
            continue

        tasks = Task.query.filter_by(evaluation_id=evaluation.id).order_by(Task.id).all()
        if len(tasks) < validated["instance"]:
            msg = standard_error(f"instancia={validated['instance']}", f"solo hay {len(tasks)} tareas.")
            print(f"❌ {msg}")
            errors.append(msg)
            ignored += 1
            continue

        task = tasks[validated["instance"] - 1]
        existing = Grade.query.filter_by(student_id=student.id, task_id=task.id).first()

        if existing:
            if existing.value == validated["value"]:
                continue
            if not force:
                duplicated.append(format_grade_duplicate(existing, validated["value"]))
                print(f"🔁 Nota duplicada para alumno_id={student.id}, task_id={task.id}")
                continue
            else:
                existing.value = validated["value"]
                inserted += 1
        else:
            db.session.add(Grade(
                student_id=student.id,
                task_id=task.id,
                value=validated["value"]
            ))
            inserted += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=ignored, duplicated=duplicated, errors=errors)
