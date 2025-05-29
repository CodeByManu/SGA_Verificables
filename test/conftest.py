
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import date
from app_factory import create_app
from models import db, Course, Period, Teacher, Section, Evaluation, Task, Student, StudentSection, Grade

@pytest.fixture
def setup_database():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()

        # Curso y sección
        course = Course(code='ICC1234', name='Estática', credits=6)
        period = Period(course=course, period='2024_1')
        teacher = Teacher(name='Prof. Test', email='prof@test.cl')
        section = Section(period=period, teacher=teacher, section_number='1', evaluation_weight_type='porcentaje', open=False)

        # Evaluación y tareas
        evaluation = Evaluation(name='Proyecto', section=section, weight=100, tasks_weight_type='porcentaje')
        task1 = Task(name='Entrega 1', evaluation=evaluation, date=date.today(), weight=40)
        task2 = Task(name='Entrega 2', evaluation=evaluation, date=date.today(), weight=60)

        # Estudiantes y relaciones
        student1 = Student(name='Alice', email='alice@test.cl', admission_date=2023)
        student2 = Student(name='Bob', email='bob@test.cl', admission_date=2023)
        ss1 = StudentSection(student=student1, section=section)
        ss2 = StudentSection(student=student2, section=section)

        # Notas
        g1 = Grade(student=student1, task=task1, value=5.0)
        g2 = Grade(student=student1, task=task2, value=6.0)
        g3 = Grade(student=student2, task=task1, value=4.0)
        g4 = Grade(student=student2, task=task2, value=5.0)

        db.session.add_all([
            course, period, teacher, section, evaluation, task1, task2,
            student1, student2, ss1, ss2, g1, g2, g3, g4
        ])
        db.session.commit()

        yield section
