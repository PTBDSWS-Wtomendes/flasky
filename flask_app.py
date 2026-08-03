from flask import Flask, request, make_response, redirect, abort

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '''
    <p>Alterações por meio do PythonAnywhere -> GitHub</p>

    <table border="1">
        <tr>
            <td><b>Aluno:</b></td>
            <td>Wellington Mendes</td>
        </tr>
        <tr>
            <td><b>Prontuário:</b></td>
            <td>PT303772x</td>
        </tr>
        <tr>
            <td><b>Disciplina:</b></td>
            <td>PTBDSWS</td>
    </table>
    '''

@app.route('/user/<name>')
def user(name):
    return f'<h1>Hello, {name}!</h1>'


@app.route('/contextorequisicao')
def contextorequisicao():
    return f'<p>Your browser is {request.headers.get("User-Agent")}</p>'


@app.route('/codigostatusdiferente')
def codigostatusdiferente():
    return "<p>Bad request</p>", 400


@app.route('/objetoresposta/<name>')
def objetoresposta(name):
    response = make_response("<h1>This document carries a cookie!</h1>")
    response.set_cookie("usuario", name)
    return response

@app.route('/redirecionamento')
def redirecionamento():
    return redirect("https://ptb.ifsp.edu.br/")


@app.route('/abortar')
def abortar():
    abort(404)