# loaders/grades_loader.py
from models import db, Grade

def import_grades(data, force=False):
    notas = data.get("notas", [])
    inserted = 0
    ignored = 0
    duplicated = []

    for entry in notas:
        student_id = entry.get("alumno_id")
        task_id = entry.get("topico_id")
        nota = entry.get("nota")

        if not student_id or not task_id or nota is None:
            ignored += 1
            continue

        existing = Grade.query.filter_by(student_id=student_id, task_id=task_id).first()
        if existing:
            if not force:
                duplicated.append({
                    "ya_existe": {
                        "student_id": student_id,
                        "task_id": task_id,
                        "nota_actual": existing.value
                    },
                    "nuevo": {
                        "student_id": student_id,
                        "task_id": task_id,
                        "nota": nota
                    }
                })
                continue
            else:
                existing.value = nota
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
