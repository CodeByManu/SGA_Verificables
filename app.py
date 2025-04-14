from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Course, Prerequisite, Period, Section, Teacher, Student, StudentSection, Evaluation, Task, Grade

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

# HOME

@app.route('/')
def home():
    return render_template('home.html', active_page='home')

# COURSES

@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return render_template('courses/courses.html', courses=courses, active_page='courses')

@app.route('/courses/<int:course_id>', methods=['GET'])
def get_course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('courses/course_detail.html', course=course, active_page='courses')

@app.route('/courses', methods=['POST'])
def create_course():
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        new_course = Course(code=code, name=name, description=description)
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully!')
        return redirect(url_for('get_courses'))
    
@app.route('/courses/<int:course_id>', methods=['POST'])
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.code = request.form.get('code')
        course.name = request.form.get('name')
        course.description = request.form.get('description')
        db.session.commit()
        flash('Course updated successfully!')
        return redirect(url_for('get_courses'))
    
@app.route('/course/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Curso eliminado exitosamente.')
    return redirect(url_for('get_courses'))

#TEACHERS

@app.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    return render_template('teachers/teachers.html', teachers=teachers, active_page='teachers')

@app.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher_detail(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return render_template('teachers/teacher_detail.html', teacher=teacher, active_page='teachers')

@app.route('/teachers', methods=['POST'])
def create_teacher():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        new_teacher = Teacher(name=name, email=email)
        db.session.add(new_teacher)
        db.session.commit()
        flash('Teacher added successfully!')
        return redirect(url_for('get_teachers'))
    
@app.route('/teachers/<int:teacher_id>', methods=['POST'])
def update_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    if request.method == 'POST':
        teacher.name = request.form.get('name')
        teacher.email = request.form.get('email')
        db.session.commit()
        flash('Teacher updated successfully!')
        return redirect(url_for('get_teachers'))
    
@app.route('/teacher/delete/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully.')
    return redirect(url_for('get_teachers'))

#STUDENTS

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return render_template('students/students.html', students=students, active_page='students')

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('students/student_detail.html', student=student, active_page='students')

@app.route('/students', methods=['POST'])
def create_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        admission_date = request.form.get('admission_date')
        new_student = Student(name=name, email=email, admission_date=admission_date)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('get_students'))

@app.route('/students/<int:student_id>', methods=['POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email')
        student.admission_date = request.form.get('admission_date')
        db.session.commit()
        flash('Student updated successfully!')
        return redirect(url_for('get_students'))

@app.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.')
    return redirect(url_for('get_students'))


#PERIODS

@app.route('/periods/<int:period_id>', methods=['GET'])
def get_period_detail(period_id):
    period = Period.query.get_or_404(period_id)
    teachers = Teacher.query.all()
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
    return redirect(url_for('get_course_detail', course_id=course.id))

@app.route('/courses/<int:course_id>/periods/<int:period_id>/delete', methods=['POST'])
def delete_period(course_id, period_id):
    period = Period.query.get_or_404(period_id)
    db.session.delete(period)
    db.session.commit()
    flash('Periodo eliminado correctamente.')
    return redirect(url_for('get_course_detail', course_id=course_id))

#SECTION
@app.route('/sections/<int:section_id>', methods=['GET'])
def get_section_detail(section_id):
    section = Section.query.get_or_404(section_id)

    current_ids = [ss.student_id for ss in section.student_sections]
    available_students = Student.query.filter(Student.id.notin_(current_ids)).all()

    return render_template(
        'sections/section_detail.html',
        section=section,
        available_students=available_students,
        active_page='courses'
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


if __name__ == '__main__':
    app.run(debug=True)