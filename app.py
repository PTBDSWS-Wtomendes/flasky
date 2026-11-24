import os
from datetime import datetime, timezone

from flask import Flask, flash, redirect, render_template, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-forte-altere-em-producao')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
application = app

SEMESTRE_CHOICES = [
    ('1º semestre', '1º semestre'),
    ('2º semestre', '2º semestre'),
    ('3º semestre', '3º semestre'),
    ('4º semestre', '4º semestre'),
    ('5º semestre', '5º semestre'),
    ('6º semestre', '6º semestre'),
]


class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    semestre = db.Column(db.String(32), nullable=False)
    professores = db.relationship('Professor', backref='disciplina', lazy='dynamic')
    alunos = db.relationship('Aluno', backref='disciplina', lazy='dynamic')

    def __repr__(self):
        return f'<Disciplina {self.nome!r} ({self.semestre!r})>'


class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    disciplina_id = db.Column(
        db.Integer, db.ForeignKey('disciplinas.id'), nullable=False
    )

    def __repr__(self):
        return f'<Professor {self.nome!r}>'


class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    disciplina_id = db.Column(
        db.Integer, db.ForeignKey('disciplinas.id'), nullable=False
    )

    def __repr__(self):
        return f'<Aluno {self.nome!r}>'


class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False)
    descricao = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Curso {self.nome!r}>'


with app.app_context():
    db.create_all()


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        Disciplina=Disciplina,
        Professor=Professor,
        Aluno=Aluno,
        Curso=Curso,
    )


def _coerce_disciplina_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class DisciplinaForm(FlaskForm):
    nome = StringField(
        'Cadastre a nova disciplina e o semestre associado:',
        validators=[DataRequired(message='Informe o nome da disciplina.')],
    )
    semestre = RadioField(
        'Semestre',
        choices=SEMESTRE_CHOICES,
        validators=[DataRequired(message='Selecione o semestre associado.')],
    )
    submit = SubmitField('Cadastrar')


class ProfessorForm(FlaskForm):
    nome = StringField(
        'Cadastre o novo Professor:',
        validators=[DataRequired(message='Informe o nome do professor.')],
    )
    disciplina_id = SelectField(
        'Disciplina associada:',
        coerce=_coerce_disciplina_id,
        validators=[DataRequired(message='Selecione uma disciplina associada.')],
    )
    submit = SubmitField('Cadastrar')


class AlunoForm(FlaskForm):
    nome = StringField(
        'Cadastre o novo Aluno:',
        validators=[DataRequired(message='Informe o nome do aluno.')],
    )
    disciplina_id = SelectField(
        'Disciplina associada:',
        coerce=_coerce_disciplina_id,
        validators=[DataRequired(message='Selecione uma disciplina associada.')],
    )
    submit = SubmitField('Cadastrar')


class CursoForm(FlaskForm):
    nome = StringField(
        'Qual é o nome do curso?',
        validators=[DataRequired(message='Informe o nome do curso.')],
    )
    descricao = TextAreaField(
        'Descrição (250 caracteres)',
        validators=[
            DataRequired(message='Informe a descrição do curso.'),
            Length(max=250, message='A descrição deve ter no máximo 250 caracteres.'),
        ],
    )
    submit = SubmitField('Cadastrar')


def utc_now():
    return datetime.now(timezone.utc)


def _disciplina_choices():
    disciplinas_list = Disciplina.query.order_by(Disciplina.id).all()
    if not disciplinas_list:
        return [(0, 'Nenhuma disciplina cadastrada')]
    return [(d.id, d.nome) for d in disciplinas_list]


def _handle_associado(model, form, endpoint, title, list_heading, col_label, empty_label):
    choices = _disciplina_choices()
    form.disciplina_id.choices = choices
    has_disciplinas = choices[0][0] != 0

    if form.validate_on_submit():
        nome = form.nome.data.strip()
        disciplina = db.session.get(Disciplina, form.disciplina_id.data)
        if not nome:
            flash('Informe um nome válido.', 'warning')
        elif disciplina is None:
            flash('Cadastre ao menos uma disciplina antes de continuar.', 'warning')
        else:
            db.session.add(model(nome=nome, disciplina=disciplina))
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for(endpoint))

    items = model.query.order_by(model.id).all()
    return render_template(
        'cadastro_associado.html',
        title=title,
        list_heading=list_heading,
        col_label=col_label,
        empty_label=empty_label,
        form=form,
        items=items,
        has_disciplinas=has_disciplinas,
    )


@app.route('/')
def index():
    return render_template(
        'index.html',
        student_name='Wellington Mendes',
        registration='PT303772X',
        current_time=utc_now(),
    )


@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    form = DisciplinaForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        if not nome:
            flash('Informe um nome válido para a disciplina.', 'warning')
            return redirect(url_for('disciplinas'))

        existing = Disciplina.query.filter_by(nome=nome).first()
        if existing is not None:
            flash('Disciplina já cadastrada.', 'warning')
        else:
            disciplina = Disciplina(nome=nome, semestre=form.semestre.data)
            db.session.add(disciplina)
            db.session.commit()
            flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('disciplinas'))

    disciplinas_cadastradas = Disciplina.query.order_by(Disciplina.id).all()
    return render_template(
        'disciplinas.html',
        form=form,
        disciplinas=disciplinas_cadastradas,
    )


@app.route('/professores', methods=['GET', 'POST'])
def professores():
    return _handle_associado(
        model=Professor,
        form=ProfessorForm(),
        endpoint='professores',
        title='Cadastro de Professores | Avaliação semestral',
        list_heading='Relação de professores cadastrados',
        col_label='Professor',
        empty_label='Nenhum professor cadastrado.',
    )


@app.route('/alunos', methods=['GET', 'POST'])
def alunos():
    return _handle_associado(
        model=Aluno,
        form=AlunoForm(),
        endpoint='alunos',
        title='Cadastro de Alunos | Avaliação semestral',
        list_heading='Relação de alunos cadastrados',
        col_label='Aluno',
        empty_label='Nenhum aluno cadastrado.',
    )


@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    form = CursoForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        descricao = form.descricao.data.strip()
        if not nome or not descricao:
            flash('Preencha o nome e a descrição do curso.', 'warning')
            return redirect(url_for('cursos'))

        existing = Curso.query.filter_by(nome=nome).first()
        if existing is not None:
            flash('Curso já cadastrado.', 'warning')
        else:
            db.session.add(Curso(nome=nome, descricao=descricao))
            db.session.commit()
            flash('Curso cadastrado com sucesso!', 'success')
        return redirect(url_for('cursos'))

    cursos_cadastrados = Curso.query.order_by(Curso.id).all()
    return render_template(
        'cursos.html',
        form=form,
        cursos=cursos_cadastrados,
    )


@app.route('/ocorrencias')
def ocorrencias():
    return render_template('nao_disponivel.html', current_time=utc_now())


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
