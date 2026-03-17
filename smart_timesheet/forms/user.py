from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    DateField,
    TextAreaField,
    TimeField,
    SelectField,
    BooleanField,
)
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from smart_timesheet.models import User, Project, Task, TaskStatus


class LoginForm(FlaskForm):
    username = StringField(
        'Username or Email',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember = BooleanField("Remember Me")

    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters"),
            Regexp(
                r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).+$',
                message="Password must contain uppercase, lowercase, number and special character"
            )
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )

    submit = SubmitField('Register')


class UserForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    submit = SubmitField('Save')


class ProjectForm(FlaskForm):
    title = StringField(
        'Project Title',
        validators=[DataRequired()]
    )

    submit = SubmitField('Save')


class TaskForm(FlaskForm):
    title = StringField(
        'Task Title',
        validators=[DataRequired()]
    )

    project = QuerySelectField(
        'Project',
        query_factory=lambda: Project.query.all(),
        get_label='title',
        allow_blank=False,
        validators=[DataRequired()]
    )

    assigned_users = QuerySelectMultipleField(
        'Assign Users',
        query_factory=lambda: User.query.all(),
        get_label='username',
        allow_blank=True
    )

    submit = SubmitField('Save')


class TimesheetForm(FlaskForm):
    # user = QuerySelectField(
    #     'User',
    #     query_factory=lambda: User.query.all(),
    #     get_label='username',
    #     validators=[DataRequired()]
    # )

    project = QuerySelectField(
        'Project',
        query_factory=lambda: Project.query.all(),
        get_label='title',
        validators=[DataRequired()]
    )

    task = QuerySelectField(
        'Task',
        query_factory=lambda: Task.query.all(),
        get_label='title',
        validators=[DataRequired()]
    )

    date = DateField(
        'Date',
        validators=[DataRequired()]
    )

    from_time = TimeField(
        'From Time',
        validators=[DataRequired()]
    )

    to_time = TimeField(
        'To Time',
        validators=[DataRequired()]
    )

    description = TextAreaField(
        'Description',
        validators=[DataRequired()]
    )

    status = SelectField(
        'Status',
        choices=[(status.name, status.value) for status in TaskStatus],
        validators=[DataRequired()]
    )

    submit = SubmitField('Save')
