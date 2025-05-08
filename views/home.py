from services.home_service import get_basic_counts, get_period_summary, get_grade_statistics
from flask import Blueprint, render_template, request, redirect, url_for, flash

home_bp = Blueprint('home', __name__)
@home_bp.route('/')
def home():
    data = get_basic_counts()
    periods_data = get_period_summary()
    grade_ranges = get_grade_statistics()

    return render_template(
        'home.html',
        active_page='home',
        courses=data['courses'],
        teachers=data['teachers'],
        students=data['students'],
        period_labels=sorted(periods_data.keys()),
        period_values=[periods_data[p] for p in sorted(periods_data)],
        grade_labels=list(grade_ranges.keys()),
        grade_values=list(grade_ranges.values()),
        recent_activities=[...]  # si lo deseas puedes mover eso también
    )
