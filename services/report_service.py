from models import Section, Task, Grade, Student, StudentSection

def generate_section_final_report_text(section_id):
    section = Section.query.get_or_404(section_id)
    if section.open:
        raise ValueError("La sección aún no está cerrada.")

    lines = []
    evaluations = section.evaluations
    final_grades = []

    for ss in section.student_sections:
        student = ss.student
        line = build_student_line_with_evaluations(student, evaluations)
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

def build_student_line_with_evaluations(student, evaluations):
    line_parts = [student.name]
    for evaluation in evaluations:
        task_grades = [
            g.value for task in evaluation.tasks
            for g in student.grades if g.task_id == task.id
        ]
        avg = round(sum(task_grades) / len(task_grades), 2) if task_grades else 0.0
        grades_str = ", ".join(f"{g:.1f}" for g in task_grades)
        line_parts.append(f"{evaluation.name}: [{grades_str}] → {avg:.2f}")
    return line_parts

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

    min_grade = min(values)
    max_grade = max(values)
    avg_grade = round(sum(values) / len(values), 2)

    lines.append("\nResumen de notas:")
    lines.append(f"Nota mínima: {min_grade:.2f}")
    lines.append(f"Nota máxima: {max_grade:.2f}")
    lines.append(f"Promedio general: {avg_grade:.2f}")

    return "\n".join(lines)

def generate_student_certificate_text(student_id):
    student = Student.query.get_or_404(student_id)
    student_sections = StudentSection.query.filter_by(student_id=student_id).all()

    if not student_sections:
        raise ValueError("Este alumno no tiene cursos registrados.")

    lines = [f"Certificado de notas para: {student.name}", f"Email: {student.email}", ""]

    for ss in student_sections:
        section = ss.section
        if not section or section.open:
            continue

        course = section.period.course
        period_label = section.period.period
        final = ss.final_grade or 0.0

        lines.append(f"{course.name} ({course.code}) - Sección {section.section_number} - {period_label}")
        lines.append(f"Nota final: {final:.2f}\n")

        for evaluation in section.evaluations:
            lines.extend(build_evaluation_block(student, evaluation))

        lines.append("")

    return "\n".join(lines)

def build_evaluation_block(student, evaluation):
    task_grades = []
    task_lines = []

    for task in evaluation.tasks:
        grade = next((g.value for g in student.grades if g.task_id == task.id), None)
        if grade is not None:
            task_grades.append(grade)
            task_lines.append(f" - {task.name}: {grade:.2f}")

    if task_grades:
        avg = round(sum(task_grades) / len(task_grades), 2)
        header = f"Evaluación: {evaluation.name} → Promedio: {avg:.2f}"
        return [header] + task_lines + [""]
    return []
