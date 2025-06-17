import pandas as pd
from io import BytesIO
from services.report_service import generate_student_certificate_excel

def test_generate_student_certificate_excel(setup_database):
    section = setup_database
    student = section.student_sections[0].student

    content = generate_student_certificate_excel(student.id)
    df = pd.read_excel(BytesIO(content))

    assert "Curso" in df.columns
    assert "Nota" in df.columns
    assert any(df["Actividad"] == "Nota final")
    assert any(df["Actividad"].str.contains("Proyecto"))
    assert any(df["Actividad"].str.contains("Entrega 1"))
    assert any(df["Actividad"].str.contains("Entrega 2"))