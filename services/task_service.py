from models import db
from models.entities import Task
from flask import flash
from datetime import datetime

def create_task(evaluation_id, form_data):
    name = form_data.get('name')
    date_str = form_data.get('date')
    weight = form_data.get('weight')
    is_optional = bool(form_data.get('is_optional'))

    if not (name and date_str and weight):
        flash('Todos los campos son obligatorios.', 'danger')
        return False

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        weight = float(weight)
    except ValueError:
        flash('Fecha o peso inválido.', 'danger')
        return False

    new_task = Task(
        evaluation_id=evaluation_id,
        name=name,
        date=date,
        weight=weight,
        is_optional=is_optional
    )
    db.session.add(new_task)
    db.session.commit()
    return True

def delete_task_by_id(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
