from flask import Flask, abort, flash, make_response, redirect, render_template, request, session, url_for
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-forte-altere-em-producao'
moment = Moment(app)
application = app


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))


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