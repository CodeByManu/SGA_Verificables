from models import db
from models.entities import Evaluation

def create_evaluation_for_section(section_id, form_data):
    tasks_weight_type = form_data.get('tasks_weight_type')
    weight = form_data.get('weight')
    name = form_data.get('name')

    if not (tasks_weight_type and weight and name):
        return False

    new_evaluation = Evaluation(
        name=name,
        section_id=section_id,
        tasks_weight_type=tasks_weight_type,
        weight=weight
    )
    db.session.add(new_evaluation)
    db.session.commit()
    return True

def update_evaluation(evaluation_id, form_data):
    evaluation = Evaluation.query.get_or_404(evaluation_id)

    name = form_data.get('name')
    tasks_weight_type = form_data.get('tasks_weight_type')
    weight = form_data.get('weight')

    if name and tasks_weight_type and weight:
        evaluation.name = name
        evaluation.tasks_weight_type = tasks_weight_type
        evaluation.weight = weight
        db.session.commit()
        return True
    return False


def delete_evaluation_by_id(evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    db.session.delete(evaluation)
    db.session.commit()
