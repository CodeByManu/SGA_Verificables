from models import db, StudentSection
from services.final_grade_service import calculate_final_grades

def test_calculate_final_grades(setup_database):
    section = setup_database
    calculate_final_grades(section.id)

    ss1 = db.session.get(StudentSection, 1)
    ss2 = db.session.get(StudentSection, 2)

    assert round(ss1.final_grade, 2) == 5.6
    assert round(ss2.final_grade, 2) == 4.6
