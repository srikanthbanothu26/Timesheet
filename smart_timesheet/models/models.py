from smart_timesheet.db import db
from flask_login import UserMixin
import enum

# -----------------------------
# TASK ASSIGNED USERS TABLE
# -----------------------------
task_users = db.Table(
    'task_users',

    db.Column('task_id',
              db.Integer,
              db.ForeignKey('tasks.id'),
              primary_key=True),

    db.Column('user_id',
              db.Integer,
              db.ForeignKey('users.id'),
              primary_key=True)
)


# -----------------------------
# ENUM STATUS
# -----------------------------
class TaskStatus(enum.Enum):
    initiated = "initiated"
    completed = "completed"
    cancelled = "cancelled"


# -----------------------------
# USER
# -----------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)

    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    is_internal_user = db.Column(db.Boolean, nullable=True, default=False)

    # one2many
    timesheets = db.relationship('TimeSheet', backref='user', lazy=True)

    # tasks assigned to user
    tasks = db.relationship(
        'Task',
        secondary=task_users,
        back_populates='users'
    )

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password


# -----------------------------
# PROJECT
# -----------------------------
class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)

    # one2many
    tasks = db.relationship('Task', backref='project', lazy=True)
    timesheets = db.relationship('TimeSheet', backref='project', lazy=True)


# -----------------------------
# TASK
# -----------------------------
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)

    # many2one
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    # one2many
    timesheets = db.relationship('TimeSheet', backref='task', lazy=True)

    # assigned users
    users = db.relationship(
        'User',
        secondary=task_users,
        back_populates='tasks'
    )


# -----------------------------
# TIMESHEET
# -----------------------------
class TimeSheet(db.Model):
    __tablename__ = 'timesheets'

    id = db.Column(db.Integer, primary_key=True)

    # many2one
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    from_time = db.Column(db.Time, nullable=False)
    to_time = db.Column(db.Time, nullable=False)

    description = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.initiated
    )
