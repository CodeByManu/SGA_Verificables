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
def post_course():
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
def post_teacher():
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
def post_student():
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

if __name__ == '__main__':
    app.run(debug=True)