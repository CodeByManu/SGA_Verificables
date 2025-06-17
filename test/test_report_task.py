import pandas as pd
from io import BytesIO
from services.report_service import generate_task_grades_report_excel

def test_generate_task_grades_report_excel(setup_database):
    section = setup_database
    task = section.evaluations[0].tasks[0]

    content = generate_task_grades_report_excel(task.id)
    sheets = pd.read_excel(BytesIO(content), sheet_name=["Notas", "Resumen"])

    notas_df = sheets["Notas"]
    resumen_df = sheets["Resumen"]

    assert set(notas_df["Estudiante"]) == {"Alice", "Bob"}
    assert task.name in notas_df.columns
    assert "Promedio general" in resumen_df["Métrica"].values