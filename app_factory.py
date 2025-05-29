from flask import Flask
from config import Config
from models import db
from views import (
    student_bp, teacher_bp, course_bp, period_bp,
    section_bp, evaluation_bp, grades_bp,
    task_bp, student_section_bp, home_bp,
    file_uploads_bp, schedule_bp, report_bp
)

def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True

    db.init_app(app)

    for bp in [
        student_bp, teacher_bp, course_bp, period_bp,
        section_bp, evaluation_bp, grades_bp, task_bp,
        student_section_bp, home_bp, schedule_bp, report_bp
    ]:
        app.register_blueprint(bp)

    app.register_blueprint(file_uploads_bp, url_prefix='/upload')

    with app.app_context():
        db.create_all()

    return app
