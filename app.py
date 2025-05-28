from flask import Flask
from config import Config
from models import db 
from views import (
    student_bp, teacher_bp, course_bp, period_bp,
    section_bp, evaluation_bp, grades_bp,
    task_bp, student_section_bp, home_bp,
    file_uploads_bp, schedule_bp, report_bp
)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

for bp in [
    student_bp, teacher_bp, course_bp, period_bp,
    section_bp, evaluation_bp, grades_bp, task_bp, 
    student_section_bp, home_bp, schedule_bp, report_bp
]:
    app.register_blueprint(bp)

app.register_blueprint(file_uploads_bp, url_prefix='/upload')

if __name__ == '__main__':
    app.run(debug=True)