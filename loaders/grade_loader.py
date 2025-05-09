from models import db, Grade, Task, Student, Evaluation

def validate_grade_entry(entry):
    student_id = entry.get("alumno_id")
    evaluation_id = entry.get("topico_id")  # ahora topico_id se refiere a evaluation.id
    instance = entry.get("instancia")
    grade_value = entry.get("nota")

    if not student_id or not evaluation_id or not instance:
        return None, "Faltan 'alumno_id', 'topico_id' o 'instancia'."
    if grade_value is None:
        return None, "Falta valor de nota."
    return {
        "student_id": student_id,
        "evaluation_id": evaluation_id,
        "instance": instance,
        "value": grade_value
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

    seen = set()  # para detectar duplicados exactos en el mismo archivo

    for entry in raw_grades:
        validated, error = validate_grade_entry(entry)
        if error:
            ignored += 1
            msg = f"Entrada inválida (alumno_id={entry.get('alumno_id')}, topico_id={entry.get('topico_id')}, instancia={entry.get('instancia')}): {error}"
            print(f"⚠️ {msg}")
            errors.append(msg)
            continue

        key = (validated["student_id"], validated["evaluation_id"], validated["instance"])
        if key in seen:
            ignored += 1
            msg = f"❌ Dato repetido en archivo: alumno_id={key[0]}, topico_id={key[1]}, instancia={key[2]}"
            print(msg)
            errors.append(msg)
            continue
        seen.add(key)

        student = Student.query.get(validated["student_id"])
        if not student:
            ignored += 1
            msg = f"❌ Alumno con id={validated['student_id']} no existe."
            print(msg)
            errors.append(msg)
            continue

        evaluation = Evaluation.query.get(validated["evaluation_id"])
        if not evaluation:
            ignored += 1
            msg = f"❌ Evaluación con id={validated['evaluation_id']} no existe."
            print(msg)
            errors.append(msg)
            continue

        tasks = Task.query.filter_by(evaluation_id=evaluation.id).order_by(Task.id).all()

        if len(tasks) < validated["instance"]:
            ignored += 1
            msg = f"❌ El tópico {validated['evaluation_id']} no tiene una instancia #{validated['instance']}. Solo hay {len(tasks)}."
            print(msg)
            errors.append(msg)
            continue

        task = tasks[validated["instance"] - 1]  # instancia 1-indexed

        existing = Grade.query.filter_by(student_id=student.id, task_id=task.id).first()
        if existing:
            if existing.value == validated["value"]:
                continue
            if not force:
                duplicated.append(format_grade_duplicate(existing, validated["value"]))
                msg = f"🔁 Nota duplicada para alumno_id={student.id}, task_id={task.id}, nota existente={existing.value}, nueva={validated['value']}"
                print(msg)
                continue
            else:
                existing.value = validated["value"]
                inserted += 1
        else:
            grade = Grade(student_id=student.id, task_id=task.id, value=validated["value"])
            db.session.add(grade)
            inserted += 1

    db.session.commit()
    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated,
        "errors": errors
    }
