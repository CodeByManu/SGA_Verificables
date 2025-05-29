from services.report_service import generate_student_certificate_text

def test_generate_student_certificate_text(setup_database):
    section = setup_database
    student = section.student_sections[0].student

    report = generate_student_certificate_text(student.id)

    assert "Certificado de notas para: Alice" in report
    assert "Email: alice@test.cl" in report
    assert "Estática (ICC1234)" in report
    assert "Nota final:" in report
    assert "Evaluación: Proyecto" in report
    assert "Entrega 1" in report
    assert "Entrega 2" in report
