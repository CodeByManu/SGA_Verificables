from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db 
from models.entities import (
    Course, Prerequisite, Period, Section,
    Teacher, Student, StudentSection,
    Evaluation, Task, Grade
)
from datetime import datetime


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()
    
from views import student_bp, teacher_bp, course_bp

app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(course_bp)


# HOME

@app.route('/')
def home():
    courses = Course.query.all()
    teachers = Teacher.query.all()
    students = Student.query.all()
    
    periods_data = {}
    periods = Period.query.all()
    for period in periods:
        period_name = period.period
        if period_name in periods_data:
            periods_data[period_name] += 1
        else:
            periods_data[period_name] = 1
    
    period_labels = sorted(periods_data.keys())
    period_values = [periods_data[period] for period in period_labels]
    

    grades = Grade.query.all()
    grade_ranges = {
        'Excelente (9-10)': 0,
        'Bueno (7-8.9)': 0,
        'Regular (6-6.9)': 0,
        'Insuficiente (<6)': 0
    }
    
    for grade in grades:
        value = grade.value
        if value >= 9:
            grade_ranges['Excelente (9-10)'] += 1
        elif value >= 7:
            grade_ranges['Bueno (7-8.9)'] += 1
        elif value >= 6:
            grade_ranges['Regular (6-6.9)'] += 1
        else:
            grade_ranges['Insuficiente (<6)'] += 1
    
    grade_labels = list(grade_ranges.keys())
    grade_values = list(grade_ranges.values())

    recent_activities = [
        {
            'type': 'course',
            'icon': 'fa-plus',
            'color': 'teal',
            'message': 'Nuevo curso añadido: Programación Avanzada',
            'time': 'Hace 2 horas'
        },
        {
            'type': 'evaluation',
            'icon': 'fa-pencil-alt',
            'color': 'blue',
            'message': 'Evaluación creada: Parcial Final de Matemáticas',
            'time': 'Hace 1 día'
        },
        {
            'type': 'enrollment',
            'icon': 'fa-user-plus',
            'color': 'green',
            'message': '5 nuevos estudiantes matriculados en Física I',
            'time': 'Hace 2 días'
        }
    ]
    
    return render_template(
        'home.html', 
        active_page='home',
        courses=courses, 
        teachers=teachers, 
        students=students,
        period_labels=period_labels,
        period_values=period_values,
        grade_labels=grade_labels,
        grade_values=grade_values,
        recent_activities=recent_activities
    )


#PERIODS

@app.route('/periods/<int:period_id>', methods=['GET'])
def get_period_detail(period_id):
    period = Period.query.get_or_404(period_id)
    teachers = Teacher.query.all()
    print(teachers)

    return render_template('periods/period_detail.html', period=period, teachers=teachers, active_page='courses')

@app.route('/courses/<int:course_id>/periods', methods=['POST'])
def create_period(course_id):
    course = Course.query.get_or_404(course_id)
    period_value = request.form.get('period')
    if period_value:
        new_period = Period(course_id=course.id, period=period_value)
        db.session.add(new_period)
        db.session.commit()
        flash('Periodo agregado correctamente.')
    else:
        flash('Debes ingresar un nombre de periodo.')
    return redirect(url_for('courses.get_course_detail', course_id=course.id))

@app.route('/courses/<int:course_id>/periods/<int:period_id>/delete', methods=['POST'])
def delete_period(course_id, period_id):
    period = Period.query.get_or_404(period_id)
    db.session.delete(period)
    db.session.commit()
    flash('Periodo eliminado correctamente.')
    return redirect(url_for('courses.get_course_detail', course_id=course_id))

#SECTION

@app.route('/sections/<int:section_id>', methods=['GET'])
def get_section_detail(section_id):
    section = Section.query.get_or_404(section_id)

    current_ids = [ss.student_id for ss in section.student_sections]
    available_students = Student.query.filter(Student.id.notin_(current_ids)).all()
    
    now = datetime.now().date()

    return render_template(
        'sections/section_detail.html',
        section=section,
        available_students=available_students,
        active_page='courses',
        now=now
    )

@app.route('/sections/<int:section_id>/tasks/<int:task_id>/grading', methods=['GET', 'POST'])
def task_grading(section_id, task_id):
    section = Section.query.get_or_404(section_id)
    task = Task.query.get_or_404(task_id)
    
    if task.evaluation.section_id != section_id:
        flash('La tarea no pertenece a esta sección.', 'danger')
        return redirect(url_for('get_section_detail', section_id=section_id))
    
    student_ids = [s.student_id for s in StudentSection.query.filter_by(section_id=section_id).all()]
    students = Student.query.filter(Student.id.in_(student_ids)).all()
    
    existing_grades = {}
    for grade in Grade.query.filter_by(task_id=task_id).all():
        existing_grades[grade.student_id] = grade
    
    if request.method == 'POST':
        for student in students:
            grade_value = request.form.get(f'grade_{student.id}')
            
            if grade_value and grade_value.strip():
                try:
                    grade_value = float(grade_value)
                    
                    if 0 <= grade_value <= 100:
                        if student.id in existing_grades:
                            existing_grades[student.id].value = grade_value
                        else:
                            new_grade = Grade(
                                value=grade_value,
                                student_id=student.id,
                                task_id=task_id
                            )
                            db.session.add(new_grade)
                    else:
                        flash(f'La calificación para {student.name} debe estar entre 0 y 100.', 'warning')
                except ValueError:
                    flash(f'Valor inválido para la calificación de {student.name}.', 'warning')
        
        db.session.commit()
        flash('Calificaciones guardadas correctamente.', 'success')
        return redirect(url_for('task_grading', section_id=section_id, task_id=task_id))
    
    return render_template(
        'grades/task_grades.html',
        section=section,
        task=task,
        students=students,
        existing_grades=existing_grades
    )

@app.route('/periods/<int:period_id>/sections', methods=['POST'])
def create_section(period_id):
    period = Period.query.get_or_404(period_id)
    section_number = request.form.get('section_number')
    teacher_id = request.form.get('teacher_id')
    evaluation_weight_type = request.form.get('evaluation_weight_type')

    teacher = Teacher.query.get(teacher_id)
    if section_number and teacher:
        new_section = Section(
            period_id=period.id,
            section_number=section_number,
            teacher_id=teacher.id,
            evaluation_weight_type=evaluation_weight_type
            
        )
        db.session.add(new_section)
        db.session.commit()
        flash('Sección creada correctamente.')
    else:
        flash('Debes ingresar todos los campos requeridos.')
    return redirect(url_for('get_period_detail', period_id=period.id))


@app.route('/periods/<int:period_id>/sections/<int:section_id>/delete', methods=['POST'])
def delete_section(period_id, section_id):
    section = Section.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()
    flash('Sección eliminada correctamente.')
    return redirect(url_for('get_period_detail', period_id=period_id))

#EVALUATIONS

@app.route('/sections/<int:section_id>/evaluations', methods=['POST'])
def create_evaluation(section_id):
    section = Section.query.get_or_404(section_id)
    tasks_weight_type = request.form.get('tasks_weight_type')
    weight = request.form.get('weight')
    name = request.form.get('name')

    if tasks_weight_type and weight:
        new_evaluation = Evaluation(
            name=name,
            section_id=section.id,
            tasks_weight_type=tasks_weight_type,
            weight=weight
        )
        db.session.add(new_evaluation)
        db.session.commit()
        flash('Evaluación creada correctamente.')
    else:
        flash('Todos los campos son obligatorios.')
    
    return redirect(url_for('get_section_detail', section_id=section.id))

@app.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/delete', methods=['POST'])
def delete_evaluation(section_id, evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    db.session.delete(evaluation)
    db.session.commit()
    flash('Evaluación eliminada correctamente.')
    return redirect(url_for('get_section_detail', section_id=section_id))

#STUDENT SECTIONS

@app.route('/sections/<int:section_id>/add_students', methods=['POST'])
def add_students_to_section(section_id):
    section = Section.query.get_or_404(section_id)
    selected_ids = request.form.getlist('student_ids')

    for student_id in selected_ids:
        exists = StudentSection.query.filter_by(
            student_id=student_id,
            section_id=section.id
        ).first()
        if not exists:
            db.session.add(StudentSection(student_id=student_id, section_id=section.id))

    db.session.commit()
    flash('Estudiantes agregados correctamente.')
    return redirect(url_for('get_section_detail', section_id=section.id))

#TASKS

@app.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/tasks', methods=['POST'])
def add_task_to_evaluation(section_id, evaluation_id):

    form_evaluation_id = request.form.get('evaluation_id')
    if form_evaluation_id:
        evaluation_id = int(form_evaluation_id)
        
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    name = request.form.get('name')
    date = request.form.get('date')
    weight = request.form.get('weight')
    is_optional = bool(request.form.get('is_optional'))

    if name and date and weight:
        new_task = Task(
            evaluation_id=evaluation.id,
            name=name,
            date=date,
            weight=weight,
            is_optional=is_optional
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Tarea agregada correctamente.')
    else:
        flash('Todos los campos son obligatorios.')
    return redirect(url_for('get_section_detail', section_id=section_id))

@app.route('/sections/<int:section_id>/evaluations/<int:evaluation_id>/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(section_id, evaluation_id, task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada correctamente.')
    return redirect(url_for('get_section_detail', section_id=section_id))


if __name__ == '__main__':
    app.run(debug=True)