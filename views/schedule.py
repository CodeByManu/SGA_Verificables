from flask import Blueprint, send_file, current_app
from flask import flash, redirect, url_for
from services.schedule_service import generate_schedule

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/download_schedule')
def download_schedule():
    success = generate_schedule()
    if not success:
        flash('No hay solución factible con estas restricciones.', 'evaluation_error')
        return redirect(url_for('courses.get_courses'))
    return send_file(
        'horario_semestre.xlsx',
        as_attachment=True,
        download_name='horario_semestre.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )