from models import db, Student, Section, StudentSection

def import_students_by_section(data, force=False):
    relaciones = data.get("alumnos_seccion", [])
    inserted = 0
    ignored = 0
    duplicated = []

    # Agrupar relaciones por seccion_id si se usará force
    secciones_afectadas = set()

    for rel in relaciones:
        student_id = rel.get("alumno_id")
        section_id = rel.get("seccion_id")

        if not student_id or not section_id:
            ignored += 1
            continue

        secciones_afectadas.add(section_id)

    # Si force=True, eliminamos relaciones previas para esas secciones
    if force:
        for seccion_id in secciones_afectadas:
            StudentSection.query.filter_by(section_id=seccion_id).delete()
        db.session.flush()  # asegura que queden listas para nuevas inserciones

    # Volver a procesar relaciones después de limpiar
    for rel in relaciones:
        student_id = rel.get("alumno_id")
        section_id = rel.get("seccion_id")

        student = Student.query.get(student_id)
        section = Section.query.get(section_id)

        if not student or not section:
            ignored += 1
            continue

        exists = StudentSection.query.filter_by(student_id=student.id, section_id=section.id).first()
        if exists:
            duplicated.append({
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
            })
            continue

        relation = StudentSection(student_id=student.id, section_id=section.id)
        db.session.add(relation)
        inserted += 1

    db.session.commit()
    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated
    }
