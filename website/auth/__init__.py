from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from flask_login.utils import login_required
# Import db
from website import db

from website.models import User
from website.forms import LoginForm, RegistrationForm

auth =  Blueprint('auth', __name__, template_folder='templates')

""" ROUTES / AUTH """
@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        if form.username.data != 'ricardosaca':
            flash('You are not allowed to login')
        login_user(user, remember=form.remember_me.data)
        return redirect('/admin')
    return render_template('login.html', title='Sign In', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.username.data != 'ricardosaca':
            flash('You are not allowed to register')
            return redirect(url_for('auth.register'))
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are a now a registered user!')
            return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))