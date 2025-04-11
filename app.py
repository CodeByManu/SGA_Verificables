from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config # type: ignore
from models import db, Course, Prerequisite, Period, Section, Teacher, Student, StudentSection, Evaluation, Task, Grade # type: ignore

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)