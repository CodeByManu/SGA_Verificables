from models import Section, Task, Grade

def generate_section_final_report_text(section_id):
    section = Section.query.get_or_404(section_id)
    if section.open:
        raise ValueError("La sección aún no está cerrada.")

    lines = []
    evaluations = section.evaluations
    final_grades = []

    for ss in section.student_sections:
        student = ss.student
        line = [student.name]

        for evaluation in evaluations:
            task_grades = []
            for task in evaluation.tasks:
                grade = next(
                    (g.value for g in student.grades if g.task_id == task.id),
                    None
                )
                if grade is not None:
                    task_grades.append(grade)

            task_count = len(task_grades)
            avg = round(sum(task_grades) / task_count, 2) if task_count > 0 else 0.0
            grades_str = ", ".join(f"{g:.1f}" for g in task_grades)
            line.append(f"{evaluation.name}: [{grades_str}] → {avg:.2f}")

        final_grade = ss.final_grade or 0.0
        final_grades.append(final_grade)
        line.append(f"Nota final: {final_grade:.2f}")
        lines.append(" - ".join(line))

    if final_grades:
        min_grade = min(final_grades)
        max_grade = max(final_grades)
        avg_grade = round(sum(final_grades) / len(final_grades), 2)
        lines.append("\nResumen de notas finales:")
        lines.append(f"Nota mínima: {min_grade:.2f}")
        lines.append(f"Nota máxima: {max_grade:.2f}")
        lines.append(f"Promedio general: {avg_grade:.2f}")

    return "\n".join(lines)

def generate_task_grades_report_text(task_id):
    task = Task.query.get_or_404(task_id)
    grades = Grade.query.filter_by(task_id=task_id).all()

    if not grades:
        raise ValueError("Esta tarea no tiene notas registradas.")

    lines = []
    values = []

    for grade in grades:
        student_name = grade.student.name
        value = grade.value
        values.append(value)
        lines.append(f"{student_name} - {task.name}: {value:.2f}")

    # Agregar resumen
    min_grade = min(values)
    max_grade = max(values)
    avg_grade = round(sum(values) / len(values), 2)

    lines.append("\nResumen de notas:")
    lines.append(f"Nota mínima: {min_grade:.2f}")
    lines.append(f"Nota máxima: {max_grade:.2f}")
    lines.append(f"Promedio general: {avg_grade:.2f}")

    return "\n".join(lines)