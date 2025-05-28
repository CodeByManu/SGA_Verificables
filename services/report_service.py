from models import Section

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
