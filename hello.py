from flask import Flask, request, make_response, redirect, abort

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '''
    <p>Alterações por meio do PythonAnywhere -> GitHub</p>
    <table border="1">
        <tr>
            <td><b>Professor:</b></td>
            <td>Professor Fabio Teixeira</td>
        </tr>
        <tr>
            <td><b>Prontuário:</b></td>
            <td>PT23820X</td>
        </tr>
    </table>
    '''

@app.route('/user/<name>')
def user(name):
    return f'<h1>Hello, {name}!</h1>'


@app.route('/contextorequisicao')
def contextorequisicao():
    user_agent = request.headers.get('User-Agent')
    return f'<p>Seu navegador é: {user_agent}</p>'


@app.route('/codigostatusdiferente')
def codigostatusdiferente():
    return "<h1>Status 201</h1>", 201


@app.route('/objetoresposta')
def objetoresposta():
    resposta = make_response("<h1>Objeto Response</h1>")
    resposta.headers["Professor"] = "Fabio Teixeira"
    return resposta


@app.route('/redirecionamento')
def redirecionamento():
    return redirect('/')


@app.route('/abortar')
def abortar():
    abort(404)