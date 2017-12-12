from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm
import time

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # When this URL is sent a request, was the form submitted and were all the fields entered correctly/validated?
    if form.validate_on_submit():
        flash('your username {}'.format(form.username))
        time.sleep(2)
        return redirect('/index')
    return render_template('login.html', form=form)