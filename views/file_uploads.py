from flask import Blueprint, request, jsonify
from services.json_loader import load_json_data
from services.data_import_service import import_students

file_uploads_bp = Blueprint('file_uploads', __name__)

@file_uploads_bp.route('/students', methods=['POST'])
def upload_students():
    print("✅ Entró a upload_students")  
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="No se subió ningún archivo.")

    try:
        data = load_json_data(file)
        inserted, ignored = import_students(data)
        return jsonify(
            success=True,
            message=f"{inserted} estudiantes importados. {ignored} ignorados por datos inválidos."
        )
    except Exception as e:
        return jsonify(success=False, message=f'Error al importar estudiantes: {str(e)}')
