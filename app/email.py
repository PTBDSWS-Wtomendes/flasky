from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail

import requests
from datetime import datetime

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])    
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

def send_simple_message(to, subject, newUser):
    app = current_app._get_current_object()
    student_name = app.config.get('STUDENT_NAME') or 'Wellington Mendes'
    student_prontuario = app.config.get('STUDENT_PRONTUARIO') or 'PT303772X'
    text_body = f"Novo usuário cadastrado: {newUser}\n\n{student_name}\n{student_prontuario}"

    print('Enviando mensagem (POST)...', flush=True)
    print('URL: ' + str(app.config.get('API_URL')), flush=True)
    print('api: ' + str(app.config.get('API_KEY')), flush=True)
    print('from: ' + str(app.config.get('API_FROM')), flush=True)
    print('to: ' + str(to), flush=True)
    print('subject: ' + str(app.config.get('FLASKY_MAIL_SUBJECT_PREFIX')) + ' ' + subject, flush=True)
    print('text: ' + text_body, flush=True)

    try:
        resposta = requests.post(app.config['API_URL'], 
                                 auth=("api", app.config['API_KEY']), 
                                 data={"from": app.config['API_FROM'], 
                                       "to": to, 
                                       "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject, 
                                       "text": text_body})
            
        print('Enviando mensagem (Resposta)...' + str(resposta) + ' - ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True)
        return resposta
    except Exception as e:
        print('Erro ao enviar mensagem:', e, flush=True)
        return None