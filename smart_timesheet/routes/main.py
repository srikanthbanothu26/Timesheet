from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required

from smart_timesheet import db
from smart_timesheet.forms.user import TimesheetForm, ProjectForm, TaskForm
from smart_timesheet.models import Project, Task, TimeSheet, TaskStatus, task_users

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_admin:
        timesheets = TimeSheet.query.order_by(TimeSheet.id.desc()).all()
    else:
        timesheets = TimeSheet.query.filter_by(
            user_id=current_user.id
        ).order_by(TimeSheet.id.desc()).all()

    # projects based on assigned tasks
    projects = {task.project for task in current_user.tasks}

    return render_template(
        "main/index.html",
        timesheets=timesheets,
        projects=projects,
        user=current_user
    )


@main_bp.route("/tasks/<int:project_id>")
@login_required
def get_tasks(project_id):
    tasks = Task.query.filter_by(project_id=project_id).all()

    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title
            }
            for t in tasks
        ]
    }


@main_bp.route("/display_project_tasks/<int:project_id>")
@login_required
def get_project_tasks(project_id):
    tasks = (
        Task.query
        .join(task_users)
        .filter(
            Task.project_id == project_id,
            task_users.c.user_id == current_user.id
        )
        .all()
    )

    return render_template(
        "main/display_project_tasks.html",
        tasks=tasks,
        user=current_user
    )


@main_bp.route('/create-timesheet', methods=['POST'])
@login_required
def create_timesheet():
    data = request.get_json()

    status = data.get("status", "initiated")  # default value

    timesheet = TimeSheet(
        user_id=current_user.id,
        project_id=data["project_id"],
        task_id=data["task_id"],
        date=data["date"],
        from_time=data["from_time"],
        to_time=data["to_time"],
        description=data["description"],
        status=TaskStatus[status]
    )

    db.session.add(timesheet)
    db.session.commit()

    return {"success": True}


@main_bp.route('/update-timesheet/<int:id>', methods=['POST'])
@login_required
def update_timesheet(id):
    data = request.get_json()

    timesheet = TimeSheet.query.get_or_404(id)

    timesheet.project_id = data["project_id"]
    timesheet.task_id = data["task_id"]
    timesheet.date = data["date"]
    timesheet.from_time = data["from_time"]
    timesheet.to_time = data["to_time"]
    timesheet.description = data["description"]
    timesheet.status = TaskStatus[data["status"]]

    db.session.commit()

    return {"success": True}


@main_bp.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    if current_user.is_admin:
        project_ids = Project.query.all()
    else:
        project_ids = (
            Project.query
            .join(Task)
            .join(task_users)
            .filter(task_users.c.user_id == current_user.id)
            .distinct()
            .all()
        )

    return render_template(
        'main/projects.html',
        user=current_user,
        projects=project_ids
    )


@main_bp.route('/create-project', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data)
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('main_bp.projects'))
    return render_template('main/create_project.html', form=form)


@main_bp.route('/edit_project/<int:id>', methods=['GET', 'POST'])
@login_required
def update_project(id):
    project = Project.query.get_or_404(id)

    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        project.title = form.title.data

        db.session.commit()

        return redirect(url_for('main_bp.projects'))

    return render_template(
        "main/create_project.html",
        form=form,
        project=project
    )


@main_bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if current_user.is_admin:
        task_ids = Task.query.order_by(Task.id.desc()).all()
    else:
        task_ids = sorted(current_user.tasks, key=lambda x: x.id, reverse=True)

    return render_template(
        'main/tasks.html',
        user=current_user,
        tasks=task_ids
    )


@main_bp.route('/create-task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()

    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            project_id=form.project.data.id
        )

        task.users = form.assigned_users.data

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('main_bp.tasks'))
    return render_template('main/create_task.html', form=form)


@main_bp.route('/update-task/<int:id>', methods=['GET', 'POST'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)

    form = TaskForm(obj=task)

    if form.validate_on_submit():
        task.title = form.title.data
        task.project_id = form.project.data.id

        task.users = form.assigned_users.data

        db.session.commit()

        return redirect(url_for('main_bp.tasks'))

    return render_template(
        'main/create_task.html',
        form=form,
        task=task
    )


@main_bp.route('/edit-project/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        project.title = form.title.data
        db.session.commit()
        return redirect(url_for('main_bp.projects'))

    return render_template('main/edit_project.html', project=project, form=form)


@main_bp.route("/delete-timesheet/<int:id>", methods=["DELETE"])
def delete_timesheet(id):
    timesheet = TimeSheet.query.get(id)

    if timesheet:
        db.session.delete(timesheet)
        db.session.commit()
        return {"success": True}

    return {"success": False}
