from models import db, Student, Section, StudentSection
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

def validate_students_by_section_data(data):
    if not isinstance(data, dict):
        return None, ["El archivo debe ser un objeto JSON"]

    relations = data.get("alumnos_seccion")
    if not isinstance(relations, list):
        return None, ["El campo 'alumnos_seccion' debe ser una lista de objetos"]

    return relations, None

def validate_student_section_entry(entry):
    context = f"Alumno {entry.get('alumno_id', 'N/A')} - Sección {entry.get('seccion_id', 'N/A')}"
    validated, error = validate_required_fields(entry, ['alumno_id', 'seccion_id'], context)
    if error:
        return None, error

    try:
        student_id = validate_id_parameter(entry['alumno_id'], "alumno_id")
        section_id = validate_id_parameter(entry['seccion_id'], "seccion_id")
        return {"student_id": student_id, "section_id": section_id}, None
    except FormValidationError as e:
        return None, standard_error(context, str(e))

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

def process_student_section_entry(entry):
    student = Student.query.get(entry["student_id"])
    if not student:
        return None, standard_error(f"alumno_id={entry['student_id']}", "no existe.")

    section = Section.query.get(entry["section_id"])
    if not section:
        return None, standard_error(f"seccion_id={entry['section_id']}", "no existe.")

    exists = StudentSection.query.filter_by(student_id=student.id, section_id=section.id).first()
    if exists:
        return format_student_section_duplicate(student, section), None

    relation = StudentSection(student_id=student.id, section_id=section.id)
    db.session.add(relation)
    return None, 'inserted'

def import_students_by_section(data, force=False):
    relations, structure_errors = validate_students_by_section_data(data)
    if structure_errors:
        return standard_return(errors=structure_errors)

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
        duplicate_info, result = process_student_section_entry(entry)

        if duplicate_info:
            duplicated.append(duplicate_info)
            continue
        if result == 'inserted':
            inserted += 1
        else:
            ignored += 1

    safe_commit()
    return standard_return(inserted=inserted, ignored=ignored, duplicated=duplicated, errors=errors)
