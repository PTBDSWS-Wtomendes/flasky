import os

from flask import Flask, abort, flash, make_response, redirect, render_template, request, session, url_for
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-forte-altere-em-producao'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
application = app


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


class NameForm(FlaskForm):
    name = StringField('Informe o seu nome', validators=[DataRequired()])
    surname = StringField('Informe o seu sobrenome:', validators=[DataRequired()])
    institution = StringField('Informe a sua Instituição de ensino:', validators=[DataRequired()])
    discipline = SelectField('Informe a sua disciplina:', choices=[('DSWAF5', 'DSWAF5'), ('PTBDSWS', 'PTBDSWS')], validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Usuário ou e-mail')
    password = PasswordField('Informe a sua senha')
    submit = SubmitField('Enviar')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        session['surname'] = form.surname.data
        session['institution'] = form.institution.data
        session['discipline'] = form.discipline.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), current_time=datetime.now(), remote_ip=request.remote_addr, host=request.host)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/identificacao')
def identificacao():
    return render_template(
        'identificacao.html',
        student_name='Wellington Mendes',
        registration='PT303772x',
        discipline='PTBDSWS',
    )


@app.route('/contexto')
def contexto():
    return render_template(
        'contexto.html',
        user_agent=request.headers.get('User-Agent'),
        remote_ip=request.remote_addr,
        host=request.host,
    )


@app.route('/contextorequisicao')
def contexto_requisicao_alias():
    return render_template(
        'contexto.html',
        user_agent=request.headers.get('User-Agent'),
        remote_ip=request.remote_addr,
        host=request.host,
    )


@app.route('/codigostatusdiferente')
def codigostatusdiferente():
    return render_template('error_message.html', title='Bad request', message='Bad request'), 400


@app.route('/objetoresposta', defaults={'name': None})
@app.route('/objetoresposta/<name>')
def objetoresposta(name):
    if name is None:
        name = request.args.get('name', 'desconhecido')
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('usuario', name)
    return response


@app.route('/redirecionamento')
def redirecionamento():
    return redirect('https://ptb.ifsp.edu.br/')


@app.route('/abortar')
def abortar():
    abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)