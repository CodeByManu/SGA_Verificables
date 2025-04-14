# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    prerequisites_required = db.relationship(
        'Prerequisite',
        foreign_keys='Prerequisite.required_course_id',
        back_populates='required_course',
        cascade="all, delete"
    )
    prerequisites_main = db.relationship(
        'Prerequisite',
        foreign_keys='Prerequisite.main_course_id',
        back_populates='main_course',
        cascade="all, delete"
    )
    periods = db.relationship('Period', back_populates='course', cascade="all, delete")


class Prerequisite(db.Model):
    __tablename__ = "prerequisites"
    id = db.Column(db.Integer, primary_key=True)
    main_course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    required_course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    main_course = db.relationship('Course', foreign_keys=[main_course_id], back_populates='prerequisites_main')
    required_course = db.relationship('Course', foreign_keys=[required_course_id], back_populates='prerequisites_required')


class Period(db.Model):
    __tablename__ = "periods"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    period = db.Column(db.String(50), nullable=False)

    course = db.relationship('Course', back_populates='periods')
    sections = db.relationship('Section', back_populates='period', cascade="all, delete")
    evaluations = db.relationship('Evaluation', back_populates='period', cascade="all, delete")


class Section(db.Model):
    __tablename__ = "sections"
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('periods.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    section_number = db.Column(db.String(10), nullable=False)
    evaluation_weight_type= db.Column(db.String(50))
    
    period = db.relationship('Period', back_populates='sections')
    teacher = db.relationship('Teacher', back_populates='sections')
    student_sections = db.relationship('StudentSection', back_populates='section', cascade="all, delete")


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    sections = db.relationship('Section', back_populates='teacher', cascade="all, delete")


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    admission_date = db.Column(db.Integer, nullable=False)

    student_sections = db.relationship('StudentSection', back_populates='student', cascade="all, delete")
    grades = db.relationship('Grade', back_populates='student', cascade="all, delete")


class StudentSection(db.Model):
    __tablename__ = "student_sections"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)

    student = db.relationship('Student', back_populates='student_sections')
    section = db.relationship('Section', back_populates='student_sections')


class Evaluation(db.Model):
    __tablename__ = "evaluations"
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('periods.id'), nullable=False)
    tasks_weight_type = db.Column(db.String(50))
    weight = db.Column(db.Float)

    period = db.relationship('Period', back_populates='evaluations')
    tasks = db.relationship('Task', back_populates='evaluation', cascade="all, delete")


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float)
    is_optional = db.Column(db.Boolean, default=False)

    evaluation = db.relationship('Evaluation', back_populates='tasks')
    grades = db.relationship('Grade', back_populates='task', cascade="all, delete")


class Grade(db.Model):
    __tablename__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)

    task = db.relationship('Task', back_populates='grades')
    student = db.relationship('Student', back_populates='grades')