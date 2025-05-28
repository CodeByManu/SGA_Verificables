from flask import Blueprint, Response
from services.report_service import generate_section_final_report_text, generate_task_grades_report_text

report_bp = Blueprint('reports', __name__)

@report_bp.route('/section/<int:section_id>/final_grades/download')
def download_section_final_grades_report(section_id):
    try:
        content = generate_section_final_report_text(section_id)
        return Response(
            content,
            mimetype='text/plain',
            headers={"Content-Disposition": f"attachment;filename=seccion_{section_id}_notas.txt"}
        )
    except ValueError as e:
        return Response(str(e), status=400)
    
@report_bp.route('/task/<int:task_id>/grades/download')
def download_task_grades_report(task_id):

    try:
        content = generate_task_grades_report_text(task_id)
        return Response(
            content,
            mimetype='text/plain',
            headers={"Content-Disposition": f"attachment;filename=task_{task_id}_notas.txt"}
        )
    except ValueError as e:
        return Response(str(e), status=400)
