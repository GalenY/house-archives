from flask import render_template, flash, redirect, url_for, request
from app import db
from app.main import bp
from app.main.forms import AddSongForm
from flask_login import current_user, login_required
from app.models import User, Youtube
from datetime import datetime

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html')

@bp.route('/user/<username>')
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

@bp.route('/music', methods=['GET', 'POST'])
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

@bp.route('/search_music', methods=['POST'])
@login_required
def search_music():
    pass


@bp.route('/rate-song', methods=['POST'])
@login_required
def rate_song():
    if current_user == User.query.filter(User.username.like('Galen')).first():
        return 'Galen is trying to rate a song'
    else:
        return 'Sorry you\'re not Galen'




