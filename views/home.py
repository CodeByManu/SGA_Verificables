from flask import Blueprint, render_template
from models.entities import Course, Teacher, Student, Period, Grade

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    courses = Course.query.all()
    teachers = Teacher.query.all()
    students = Student.query.all()

    periods_data = {}
    for period in Period.query.all():
        period_name = period.period
        periods_data[period_name] = periods_data.get(period_name, 0) + 1

    period_labels = sorted(periods_data.keys())
    period_values = [periods_data[label] for label in period_labels]

    grade_ranges = {
        'Excelente (9-10)': 0,
        'Bueno (7-8.9)': 0,
        'Regular (6-6.9)': 0,
        'Insuficiente (<6)': 0
    }

    for grade in Grade.query.all():
        value = grade.value
        if value >= 9:
            grade_ranges['Excelente (9-10)'] += 1
        elif value >= 7:
            grade_ranges['Bueno (7-8.9)'] += 1
        elif value >= 6:
            grade_ranges['Regular (6-6.9)'] += 1
        else:
            grade_ranges['Insuficiente (<6)'] += 1

    recent_activities = [
        {'type': 'course', 'icon': 'fa-plus', 'color': 'teal', 'message': 'Nuevo curso añadido: Programación Avanzada', 'time': 'Hace 2 horas'},
        {'type': 'evaluation', 'icon': 'fa-pencil-alt', 'color': 'blue', 'message': 'Evaluación creada: Parcial Final de Matemáticas', 'time': 'Hace 1 día'},
        {'type': 'enrollment', 'icon': 'fa-user-plus', 'color': 'green', 'message': '5 nuevos estudiantes matriculados en Física I', 'time': 'Hace 2 días'}
    ]

    return render_template('home.html',
        active_page='home',
        courses=courses,
        teachers=teachers,
        students=students,
        period_labels=period_labels,
        period_values=period_values,
        grade_labels=list(grade_ranges.keys()),
        grade_values=list(grade_ranges.values()),
        recent_activities=recent_activities
    )
