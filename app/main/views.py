from flask import render_template, redirect, url_for
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/login')
def login_redirect():
    return redirect(url_for('auth.login'))


@main.route('/register')
def register_redirect():
    return redirect(url_for('auth.register'))


@main.route('/logout')
def logout_redirect():
    return redirect(url_for('auth.logout'))
