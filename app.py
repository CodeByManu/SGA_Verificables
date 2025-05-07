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
    
from views import (
    student_bp, teacher_bp, course_bp, period_bp,
    section_bp, evaluation_bp, grades_bp,
    task_bp, student_section_bp, home_bp
)

for bp in [
    student_bp, teacher_bp, course_bp, period_bp,
    section_bp, evaluation_bp, grades_bp,
    task_bp, student_section_bp, home_bp
]:
    app.register_blueprint(bp)




if __name__ == '__main__':
    app.run(debug=True)