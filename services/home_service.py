from models.entities import Course, Teacher, Student, Period, Grade

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
        'Excelente (9-10)': 0,
        'Bueno (7-8.9)': 0,
        'Regular (6-6.9)': 0,
        'Insuficiente (<6)': 0
    }
    for grade in Grade.query.all():
        v = grade.value
        if v >= 9:
            grade_ranges['Excelente (9-10)'] += 1
        elif v >= 7:
            grade_ranges['Bueno (7-8.9)'] += 1
        elif v >= 6:
            grade_ranges['Regular (6-6.9)'] += 1
        else:
            grade_ranges['Insuficiente (<6)'] += 1
    return grade_ranges
