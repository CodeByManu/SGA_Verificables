from models import db, Student, Section, StudentSection
from utils.utils import (
    validate_required_fields,
    standard_error,
    format_duplicate,
    safe_commit,
    standard_return
)

def validate_student_section_entry(entry):
    context = f"Alumno {entry.get('alumno_id', 'N/A')} - Sección {entry.get('seccion_id', 'N/A')}"
    validated, error = validate_required_fields(entry, ['alumno_id', 'seccion_id'], context)
    if error:
        return None, error

    return {
        "student_id": entry["alumno_id"],
        "section_id": entry["seccion_id"]
    }, None

def format_student_section_duplicate(student, section):
    return format_duplicate(
        {
            "alumno_id": student.id,
            "seccion_id": section.id,
            "nombre": student.name,
            "correo": student.email
        },
        {
            "alumno_id": student.id,
            "seccion_id": section.id,
            "nombre": student.name,
            "correo": student.email
        },
        ["alumno_id", "seccion_id", "nombre", "correo"]
    )

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
            print(f"⚠️ {error}")
            errors.append(error)
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
            msg = standard_error(f"alumno_id={entry['student_id']}", "no existe.")
            print(f"❌ {msg}")
            errors.append(msg)
            ignored += 1
            continue

        if not section:
            msg = standard_error(f"seccion_id={entry['section_id']}", "no existe.")
            print(f"❌ {msg}")
            errors.append(msg)
            ignored += 1
            continue

        exists = StudentSection.query.filter_by(student_id=student.id, section_id=section.id).first()
        if exists:
            duplicated.append(format_student_section_duplicate(student, section))
            continue

        relation = StudentSection(student_id=student.id, section_id=section.id)
        db.session.add(relation)
        inserted += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=ignored, duplicated=duplicated, errors=errors)
