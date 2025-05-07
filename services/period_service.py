from models import db
from models.entities import Period, Course

def get_period_by_id(period_id):
    return Period.query.get_or_404(period_id)

def create_period_for_course(course_id, period_value):
    course = Course.query.get_or_404(course_id)
    new_period = Period(course_id=course.id, period=period_value)
    db.session.add(new_period)
    db.session.commit()

def update_period(period_id, form_data):
    period = Period.query.get_or_404(period_id)
    new_value = form_data.get('period')
    if new_value:
        period.period = new_value
        db.session.commit()
        return True
    return False


def delete_period_by_id(period_id):
    period = Period.query.get_or_404(period_id)
    db.session.delete(period)
    db.session.commit()
