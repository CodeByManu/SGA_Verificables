from flask import Blueprint, request, jsonify
from services.json_loader import load_json_data
from services.data_import_service import import_students, import_teachers, import_courses, import_students_by_section, import_periods

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
            return jsonify(success=False, duplicated=result["duplicated"], message=f"{len(result['duplicated'])} estudiantes ya existen.")
        return jsonify(success=True, message=f"{result['inserted']} estudiantes importados. {result['ignored']} ignorados.")
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
                message=f"{len(result['duplicated'])} profesores ya existen. ¿Deseas sobrescribirlos?"
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} profesores importados. {result['ignored']} ignorados."
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
                message=f"Se encontraron {len(result['duplicated'])} cursos ya existentes. ¿Deseas sobrescribirlos?"
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} cursos importados. {result['ignored']} ignorados."
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
                message=f"{len(result['duplicated'])} relaciones ya existen. ¿Deseas revisarlas?"
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} relaciones creadas. {result['ignored']} ignoradas por estar incompletas."
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
        result = import_periods(data, force=force)

        if result["duplicated"] and not force:
            return jsonify(
                success=False,
                duplicated=result["duplicated"],
                message=f"{len(result['duplicated'])} periodos ya existen. ¿Deseas sobrescribirlos?"
            )

        return jsonify(
            success=True,
            message=f"{result['inserted']} periodos creados. {result['ignored']} ignorados."
        )
    except Exception as e:
        return jsonify(success=False, message=f'Error al importar periodos: {str(e)}')
