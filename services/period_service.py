from models import db
from models.entities import Period, Course

def get_period_by_id(period_id):
    return Period.query.get_or_404(period_id)

def create_period_for_course(course_id, form_data):
    course = Course.query.get_or_404(course_id)
    period_value = form_data.get('period')
    if period_value:
        new_period = Period(course_id=course.id, period=period_value)
        db.session.add(new_period)
        db.session.commit()
    else:
        flash('Debes ingresar un nombre de periodo.')

def delete_period_by_id(period_id):
    period = Period.query.get_or_404(period_id)
    db.session.delete(period)
    db.session.commit()
