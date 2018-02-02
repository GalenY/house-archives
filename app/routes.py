from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddSongForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Youtube
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    # When this URL is sent a request, was the form submitted and were all the fields entered correctly/validated?
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        return redirect(next_page)
        # flash('dir(form.username): {}\ntype(form.username): {}\ntype(form.username.__module__): {}\n, type(form.username.gettext): {}'.format(dir(form.username), type(form.username), type(form.username.__module__), type(form.username.gettext)))
        # flash('your name is {}\n your password is {}'.format(form.username.data, form.password.data))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have succesfully registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.username != current_user.username:
        return "<h1>Forbidden</h1>"
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.route('/music', methods=['GET', 'POST'])
@login_required
def music():
    form = AddSongForm()
    if form.validate_on_submit():
        song = Youtube()
        song.set_values(form.url.data)
        db.session.add(song)
        db.session.commit()
        flash('{} was successfully added!'.format(song.title), 'alert alert-success')

    return render_template('music.html', form=form, youtubes=Youtube.query.all())

@app.route('/search_music', methods=['POST'])
@login_required
def search_music():
    pass