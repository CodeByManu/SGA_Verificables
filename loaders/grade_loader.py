from models import db, Grade, Task, Student

def import_grades(data, force=False):
    notas = data.get("notas", [])
    inserted = 0
    ignored = 0
    duplicated = []

    for entry in notas:
        student_id = entry.get("alumno_id")
        task_id = entry.get("topico_id")
        nota = entry.get("nota")

        # Verificar existencia de entidades
        task = Task.query.get(task_id)
        student = Student.query.get(student_id)

        if not task or not student or nota is None:
            ignored += 1
            continue

        existing = Grade.query.filter_by(student_id=student_id, task_id=task_id).first()
        if existing:
            if existing.value == nota:
                continue
            if not force:
                duplicated.append({
                    "ya_existe": {
                        "student_id": student_id,
                        "task_id": task_id,
                        "nota": existing.value
                    },
                    "nuevo": {
                        "student_id": student_id,
                        "task_id": task_id,
                        "nota": nota
                    }
                })
                print(f"🔁 Nota duplicada para alumno_id={student_id}, task_id={task_id}, nota existente={existing.value}, nueva={nota}")
                continue
            else:
                existing.value = nota
                inserted += 1
        else:
            grade = Grade(student_id=student_id, task_id=task_id, value=nota)
            db.session.add(grade)
            inserted += 1

    db.session.commit()
    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated
    }
