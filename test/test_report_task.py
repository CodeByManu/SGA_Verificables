from services.report_service import generate_task_grades_report_text

def test_generate_task_grades_report_text(setup_database):
    section = setup_database
    task = section.evaluations[0].tasks[0]  

    report = generate_task_grades_report_text(task.id)

    assert "Alice" in report
    assert "Bob" in report
    assert "Entrega 1" in report
    assert "Resumen de notas:" in report
    assert "Nota mínima" in report
    assert "Nota máxima" in report
    assert "Promedio general" in report