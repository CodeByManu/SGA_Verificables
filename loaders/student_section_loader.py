from models import db, Student, Section, StudentSection

def validate_student_section_entry(entry):
    student_id = entry.get("alumno_id")
    section_id = entry.get("seccion_id")

    if not student_id or not section_id:
        return None, "Faltan 'alumno_id' o 'seccion_id'."

    return {"student_id": student_id, "section_id": section_id}, None

def format_student_section_duplicate(student, section):
    return {
        "ya_existe": {
            "alumno_id": student.id,
            "seccion_id": section.id,
            "nombre": student.name,
            "correo": student.email
        },
        "nuevo": {
            "alumno_id": student.id,
            "seccion_id": section.id,
            "nombre": student.name,
            "correo": student.email
        }
    }

def import_students_by_section(data, force=False):
    relations = data.get("alumnos_seccion", [])
    inserted = 0
    ignored = 0
    duplicated = []
    errors = []

    affected_sections = set()
    valid_entries = []

    for entry in relations:
        validated, error = validate_student_section_entry(entry)
        if error:
            ignored += 1
            msg = f"Entrada inválida (alumno_id={entry.get('alumno_id')}, seccion_id={entry.get('seccion_id')}): {error}"
            print(f"⚠️ {msg}")
            errors.append(msg)
            continue
        valid_entries.append(validated)
        affected_sections.add(validated["section_id"])

    if force:
        for section_id in affected_sections:
            StudentSection.query.filter_by(section_id=section_id).delete()
        db.session.flush()

    for entry in valid_entries:
        student = Student.query.get(entry["student_id"])
        section = Section.query.get(entry["section_id"])

        if not student:
            ignored += 1
            msg = f"❌ Alumno con id={entry['student_id']} no existe."
            print(msg)
            errors.append(msg)
            continue

        if not section:
            ignored += 1
            msg = f"❌ Sección con id={entry['section_id']} no existe."
            print(msg)
            errors.append(msg)
            continue

        exists = StudentSection.query.filter_by(student_id=student.id, section_id=section.id).first()
        if exists:
            duplicated.append(format_student_section_duplicate(student, section))
            continue

        relation = StudentSection(student_id=student.id, section_id=section.id)
        db.session.add(relation)
        inserted += 1

    db.session.commit()
    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated,
        "errors": errors
    }
