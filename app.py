from datetime import datetime

from flask import Flask, abort, make_response, redirect, render_template, request
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)


@app.route('/')
def index():
    current_time = datetime.utcnow()
    return render_template('index.html', current_time=current_time)


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