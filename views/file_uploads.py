from flask import Blueprint, request, jsonify
from services.json_loader import load_json_data
from services.data_import_service import import_students, import_teachers, import_courses, import_students_by_section, import_course_periods, import_sections_with_evaluations, import_grades, import_classrooms

file_uploads_bp = Blueprint('file_uploads', __name__)

@file_uploads_bp.route('/students', methods=['POST'])
def upload_students():
    file = request.files.get('json_file')
    force = request.args.get('force', 'false').lower() == 'true'
    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")
    try:
        data = load_json_data(file)
        result = import_students(data, force=force)
        if result["duplicated"] and not force:
            return jsonify(success=False, duplicated=result["duplicated"], message=f"{len(result['duplicated'])} estudiantes ya existen.", mistakes=result.get("errors", []))
        return jsonify(success=True, message=f"{result['inserted']} estudiantes importados. {result['ignored']} ignorados.", mistakes=result.get("errors", []))
    except Exception as e:
        return jsonify(success=False, message=str(e))


@file_uploads_bp.route('/teachers', methods=['POST'])
def upload_teachers():
    print("✅ Entró a upload_teachers")
    file = request.files.get('json_file')
    force = request.args.get('force', 'false').lower() == 'true'

    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        result = import_teachers(data, force=force)

        if result["duplicated"] and not force:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"{len(result['duplicated'])} profesores ya existen. ¿Deseas sobrescribirlos?",
                mistakes=result.get("errors", [])
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} profesores importados. {result['ignored']} ignorados.",
            mistakes=result.get("errors", [])
        )

    except Exception as e:
        return jsonify(success=False, message=f'Error al importar profesores: {str(e)}')

    
@file_uploads_bp.route('/courses', methods=['POST'])
def upload_courses():
    print("✅ Entró a upload_courses")
    file = request.files.get('json_file')
    force = request.args.get('force', 'false').lower() == 'true'
    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        result = import_courses(data, force=force)

        if result["duplicated"] and not force:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"Se encontraron {len(result['duplicated'])} cursos ya existentes. ¿Deseas sobrescribirlos?",
                mistakes=result.get("errors", [])
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} cursos importados. {result['ignored']} ignorados.",
            mistakes=result.get("errors", [])
        )
    except Exception as e:
        return jsonify(success=False, message=f'Error al importar cursos: {str(e)}')


@file_uploads_bp.route('/students_section', methods=['POST'])
def upload_students_by_section():
    print("✅ Entró a upload_students_by_section")
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        force = request.args.get('force', 'false').lower() == 'true'
        result = import_students_by_section(data, force=force)

        if result["duplicated"]:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"{len(result['duplicated'])} relaciones ya existen. ¿Deseas revisarlas?",
                mistakes=result.get("errors", [])
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} relaciones creadas. {result['ignored']} ignoradas por estar incompletas.",
            mistakes=result.get("errors", [])
        )

    except Exception as e:
        return jsonify(success=False, message=f'Error al importar alumnos por sección: {str(e)}')

@file_uploads_bp.route('/periods', methods=['POST'])
def upload_course_periods():
    print("✅ Entró a upload_course_periods")
    file = request.files.get('json_file')
    force = request.args.get('force', 'false').lower() == 'true'

    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        result = import_course_periods(data, force=force)

        if result["duplicated"] and not force:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"{len(result['duplicated'])} periodos ya existen. ¿Deseas sobrescribirlos?",
                mistakes=result.get("errors", [])
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} periodos creados. {result['ignored']} ignorados.",
            mistakes=result.get("errors", [])
        )
    except Exception as e:
        return jsonify(success=False, message=f'Error al importar periodos: {str(e)}')

@file_uploads_bp.route('/sections_with_eval', methods=['POST'])
def upload_sections_with_evaluations():
    print("✅ Entró a upload_sections_with_evaluations")
    file = request.files.get('json_file')
    force = request.args.get('force', 'false').lower() == 'true'

    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        result = import_sections_with_evaluations(data, force=force)

        if result["duplicated"] and not force:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"{len(result['duplicated'])} secciones ya existen. ¿Deseas sobrescribirlas?",
                mistakes=result.get("errors", [])
            )

        return jsonify(
            success=True,
            message=f"{result['sections_inserted']} secciones creadas. {result['ignored']} ignoradas.",
            mistakes=result.get("errors", [])
        )

    except Exception as e:
        return jsonify(success=False, message=f'Error al importar secciones con evaluación: {str(e)}')

@file_uploads_bp.route('/grades', methods=['POST'])
def upload_grades():
    print("✅ Entró a upload_grades")
    file = request.files.get('json_file')
    force = request.args.get('force', 'false').lower() == 'true'

    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        result = import_grades(data, force=force)

        if result["duplicated"] and not force:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"{len(result['duplicated'])} notas ya existen. ¿Deseas sobrescribirlas?",
                mistakes=result.get("errors", [])
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} notas procesadas. {result['ignored']} ignoradas.",
            mistakes=result.get("errors", [])
        )
    except Exception as e:
        return jsonify(success=False, message=f'Error al importar notas: {str(e)}')


@file_uploads_bp.route('/classrooms', methods=['POST'])
def upload_classrooms():
    print("✅ Entró a upload_classrooms")
    file = request.files.get('json_file')
    force = request.args.get('force', 'false').lower() == 'true'

    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        result = import_classrooms(data, force=force)

        if result["duplicated"] and not force:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"{len(result['duplicated'])} salas ya existen. ¿Deseas sobrescribirlas?",
                mistakes=result.get("errors", [])
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} salas importadas. {result['ignored']} ignoradas.",
            mistakes=result.get("errors", [])
        )

    except Exception as e:
        return jsonify(success=False, message=f'Error al importar salas: {str(e)}')
