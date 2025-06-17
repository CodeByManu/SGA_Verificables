from io import BytesIO
import pandas as pd
from models import Section, Task, Grade, Student, StudentSection
from services.final_grade_service import compute_evaluation_grade

def generate_section_final_report_excel(section_id):
    section = Section.query.get_or_404(section_id)
    if section.open:
        raise ValueError("La sección aún no está cerrada.")

    evaluations = section.evaluations
    headers = ["Estudiante"] + [ev.name for ev in evaluations] + ["Nota final"]
    rows = []
    final_grades = []

    for ss in section.student_sections:
        student = ss.student
        row = [student.name]
        for ev in evaluations:
            task_grades = [
                g.value for task in ev.tasks for g in student.grades if g.task_id == task.id
            ]
            avg = round(sum(task_grades) / len(task_grades), 2) if task_grades else 0.0
            row.append(avg)
        final_grade = ss.final_grade or 0.0
        row.append(final_grade)
        final_grades.append(final_grade)
        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)

    summary_df = pd.DataFrame([
        {"Métrica": "Nota mínima", "Valor": min(final_grades) if final_grades else 0.0},
        {"Métrica": "Nota máxima", "Valor": max(final_grades) if final_grades else 0.0},
        {"Métrica": "Promedio general", "Valor": round(sum(final_grades) / len(final_grades), 2) if final_grades else 0.0},
    ])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Notas")
        summary_df.to_excel(writer, index=False, sheet_name="Resumen")
    return output.getvalue()

def generate_task_grades_report_excel(task_id):
    task = Task.query.get_or_404(task_id)
    grades = Grade.query.filter_by(task_id=task_id).all()

    if not grades:
        raise ValueError("Esta tarea no tiene notas registradas.")

    rows = []
    values = []

    for grade in grades:
        rows.append([grade.student.name, grade.value])
        values.append(grade.value)

    df = pd.DataFrame(rows, columns=["Estudiante", task.name])

    summary_df = pd.DataFrame([
        {"Métrica": "Nota mínima", "Valor": min(values)},
        {"Métrica": "Nota máxima", "Valor": max(values)},
        {"Métrica": "Promedio general", "Valor": round(sum(values) / len(values), 2)},
    ])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Notas")
        summary_df.to_excel(writer, index=False, sheet_name="Resumen")
    return output.getvalue()


def generate_student_certificate_excel(student_id):
    student = Student.query.get_or_404(student_id)
    student_sections = StudentSection.query.filter_by(student_id=student_id).all()

    if not student_sections:
        raise ValueError("Este alumno no tiene cursos registrados.")

    rows = []
    for ss in student_sections:
        section = ss.section
        if not section or section.open:
            continue

        course = section.period.course
        period_label = section.period.period
        final = ss.final_grade or 0.0

        rows.append([
            course.name,
            course.code,
            section.section_number,
            period_label,
            "Nota final",
            final,
        ])

        for evaluation in section.evaluations:
            avg = compute_evaluation_grade(student, evaluation)
            rows.append([
                course.name,
                course.code,
                section.section_number,
                period_label,
                evaluation.name,
                round(avg, 2),
            ])
            for task in evaluation.tasks:
                grade = next((g.value for g in student.grades if g.task_id == task.id), None)
                if grade is not None:
                    rows.append([
                        course.name,
                        course.code,
                        section.section_number,
                        period_label,
                        f"  {task.name}",
                        grade,
                    ])

    df = pd.DataFrame(rows, columns=["Curso", "Código", "Sección", "Periodo", "Actividad", "Nota"])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Certificado")
    return output.getvalue()