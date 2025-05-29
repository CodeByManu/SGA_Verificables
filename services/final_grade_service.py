from models import db, Section

def calculate_final_grades(section_id):
    """Calcula y guarda las notas finales de todos los estudiantes en una sección cerrada."""
    section = Section.query.get_or_404(section_id)
    if section.open:
        raise ValueError("No se puede calcular la nota final de una sección abierta.")

    for student_section in section.student_sections:
        final_grade = compute_student_final_grade(student_section)
        student_section.final_grade = round(final_grade, 2)

    db.session.commit()


def compute_student_final_grade(student_section):
    """Calcula la nota final de un estudiante en una sección según sus evaluaciones."""
    section = student_section.section
    student = student_section.student
    final_grade = 0.0
    total_eval_weight = 0.0

    for evaluation in section.evaluations:
        eval_grade = compute_evaluation_grade(student, evaluation)

        if section.evaluation_weight_type == "peso":
            eval_weight = evaluation.weight or 1.0
            final_grade += eval_grade * eval_weight
            total_eval_weight += eval_weight
        else:  # porcentaje
            eval_weight = evaluation.weight or 0.0
            final_grade += eval_grade * (eval_weight / 100.0)

    if section.evaluation_weight_type == "peso" and total_eval_weight > 0:
        final_grade /= total_eval_weight

    return final_grade


def compute_evaluation_grade(student, evaluation):
    """Calcula la nota de un estudiante en una evaluación (agrupación de tareas)."""
    eval_grade = 0.0
    total_task_weight = 0.0

    grades_by_task = {
        grade.task_id: grade.value
        for grade in student.grades
        if grade.task.evaluation_id == evaluation.id
    }

    for task in evaluation.tasks:
        grade_value = grades_by_task.get(task.id)

        if grade_value is None and not task.is_optional:
            grade_value = 0.0
        elif grade_value is None and task.is_optional:
            continue

        if evaluation.tasks_weight_type == "peso":
            task_weight = task.weight or 1.0
            eval_grade += grade_value * task_weight
            total_task_weight += task_weight
        else:  # porcentaje
            task_weight = task.weight or 0.0
            eval_grade += grade_value * (task_weight / 100.0)

    if evaluation.tasks_weight_type == "peso" and total_task_weight > 0:
        eval_grade /= total_task_weight

    return eval_grade
