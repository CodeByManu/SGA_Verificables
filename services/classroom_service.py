from models import db
from models.entities import Classroom

def get_all_classrooms():
    return Classroom.query.all()