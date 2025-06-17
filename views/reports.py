from flask import Blueprint, Response
from services.report_service import generate_section_final_report_text, generate_task_grades_report_text, generate_student_certificate_text
from services.report_service import (
    generate_section_final_report_excel,
    generate_task_grades_report_excel,
    generate_student_certificate_excel,
)

report_bp = Blueprint('reports', __name__)

@report_bp.route('/section/<int:section_id>/final_grades/download')
def download_section_final_grades_report(section_id):
    try:
        content = generate_section_final_report_excel(section_id)
        return Response(
            content,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment;filename=seccion_{section_id}_notas.xlsx"}
        )
    except ValueError as e:
        return Response(str(e), status=400)
    
@report_bp.route('/task/<int:task_id>/grades/download')
def download_task_grades_report(task_id):

    try:
        content = generate_task_grades_report_excel(task_id)
        return Response(
            content,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment;filename=task_{task_id}_notas.xlsx"}
        )
    except ValueError as e:
        return Response(str(e), status=400)
    
@report_bp.route('/student/<int:student_id>/certificate/download')
def download_student_certificate(student_id):

    try:
        content = generate_student_certificate_excel(student_id)
        return Response(
            content,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment;filename=certificado_alumno_{student_id}.xlsx"}
        )
    except ValueError as e:
        return Response(str(e), status=400)