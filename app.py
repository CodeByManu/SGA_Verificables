from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config # type: ignore
from models import db, Course, Prerequisite, Period, Section, Teacher, Student, StudentSection, Evaluation, Task, Grade # type: ignore

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses, active_page='courses')

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return render_template('students.html', students=students, active_page='students')

@app.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers, active_page='teachers')

@app.route('/courses/new', methods=['GET','POST'])
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
    return render_template('new_course.html')


if __name__ == '__main__':
    app.run(debug=True)