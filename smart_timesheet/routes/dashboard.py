from collections import defaultdict
from flask_login import current_user
from smart_timesheet.models import TimeSheet
from flask import Blueprint, render_template
from datetime import datetime

dash_bp = Blueprint('dash', __name__, url_prefix='/dash')


def calculate_hours(from_time, to_time):
    start = datetime.combine(datetime.today(), from_time)
    end = datetime.combine(datetime.today(), to_time)

    if end < start:
        return 0

    diff = end - start
    return round(diff.total_seconds() / 3600, 2)


@dash_bp.route('/dashboard')
def dashboard():
    # --------------------
    # User Timesheets
    # --------------------
    timesheets = TimeSheet.query.filter_by(
        user_id=current_user.id
    ).all()

    # --------------------
    # Daily Hours
    # --------------------
    daily_data = defaultdict(float)

    for t in timesheets:
        hours = calculate_hours(t.from_time, t.to_time)
        daily_data[str(t.date)] += hours

    daily_sorted = dict(sorted(daily_data.items()))

    dates = list(daily_sorted.keys())
    hours = list(daily_sorted.values())

    # --------------------
    # Tasks per Project
    # --------------------
    project_tasks = defaultdict(int)

    for t in timesheets:
        project_tasks[t.project.title] += 1

    project_names = list(project_tasks.keys())
    project_task_counts = list(project_tasks.values())

    # --------------------
    # Assigned Projects
    # --------------------
    assigned_projects = {task.project for task in current_user.tasks}

    # --------------------
    # Totals
    # --------------------
    total_projects = len(assigned_projects)
    total_tasks = len(current_user.tasks)
    total_hours = sum(hours)

    return render_template(
        "dashboard/dashboard.html",
        dates=dates,
        hours=hours,
        project_names=project_names,
        project_task_counts=project_task_counts,
        total_projects=total_projects,
        total_tasks=total_tasks,
        total_hours=total_hours,
        user=current_user,
    )
