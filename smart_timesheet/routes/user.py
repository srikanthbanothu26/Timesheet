from flask import Blueprint, render_template, redirect, url_for, request
from smart_timesheet.models import User
from smart_timesheet.db import db
from werkzeug.security import check_password_hash, generate_password_hash

from smart_timesheet.forms import RegisterForm, LoginForm

user_bp = Blueprint('user', __name__, url_prefix='/user')
from flask_login import login_user, login_required


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.username.data)
        ).first()

        if not user:
            form.username.errors.append("Username or email not found")

        elif not check_password_hash(user.password, form.password.data):
            form.password.errors.append("Incorrect password")
        else:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main_bp.index'))

    return render_template('user/login.html', form=form)


@login_required
@user_bp.route('/logout')
def logout():
    return redirect(url_for('user.login'))


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.login'))

    return render_template('user/register.html', form=form)


@user_bp.route('/check-email')
def check_email():
    email = request.args.get('email')

    user = User.query.filter_by(email=email).first()

    if user:
        return {"exists": True}
    return {"exists": False}


@user_bp.route('/check-username')
def check_username():
    username = request.args.get('username')

    user = User.query.filter_by(username=username).first()

    if user:
        return {"exists": True}
    return {"exists": False}


@user_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        return redirect(url_for('user.reset_password', id=user.id))
    return render_template("user/verify_email.html")


@user_bp.route('/reset-password/<int:id>', methods=['GET', 'POST'])
def reset_password(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
            user.password = generate_password_hash(password)
            return redirect(url_for('user.login'))
    return render_template('user/reset_password.html', user=user)
