from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .entities import (
    Course,
    Prerequisite,
    Period,
    Section,
    Teacher,
    Student,
    StudentSection,
    Evaluation,
    Task,
    Grade
)
