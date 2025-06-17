from models.entities import Course, Teacher, Student, Period, Grade

EXCELENT = 6.5
GOOD = 5.5
REGULAR = 4.0

def get_basic_counts():
    return {
        'courses': Course.query.all(),
        'teachers': Teacher.query.all(),
        'students': Student.query.all()
    }

def get_period_summary():
    periods = Period.query.all()
    summary = {}
    for p in periods:
        summary[p.period] = summary.get(p.period, 0) + 1
    return summary

def get_grade_statistics():
    grade_ranges = {
        'Excelente (6.5-7)': 0,
        'Bueno (5.5-6.4)': 0,
        'Regular (4-5.4)': 0,
        'Insuficiente (<4)': 0
    }
    for grade in Grade.query.all():
        v = grade.value
        if v >= EXCELENT:
            grade_ranges['Excelente (6.5-7)'] += 1
        elif v >= GOOD:
            grade_ranges['Bueno (5.5-6.4)'] += 1
        elif v >= REGULAR:
            grade_ranges['Regular (4-5.4)'] += 1
        else:
            grade_ranges['Insuficiente (<4)'] += 1
    return grade_ranges
