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

def send_simple_message(to, subject, newUser, user_email=None):
    app = current_app._get_current_object()
    student_name = app.config.get('STUDENT_NAME') or 'Wellington Mendes'
    student_prontuario = app.config.get('STUDENT_PRONTUARIO') or 'PT303772X'
    lines = [f"Novo usuário cadastrado: {newUser}"]
    if user_email:
        lines.append(f"Email inputado: {user_email}")
    lines.extend(["", student_name, student_prontuario])
    text_body = "\n".join(lines)

    print('Enviando mensagem (POST)...', flush=True)
    print('URL: ' + str(app.config.get('API_URL')), flush=True)
    print('api: ' + str(app.config.get('API_KEY')), flush=True)
    print('from: ' + str(app.config.get('API_FROM')), flush=True)
    print('to: ' + str(to), flush=True)
    print('subject: ' + str(app.config.get('FLASKY_MAIL_SUBJECT_PREFIX')) + ' ' + subject, flush=True)
    print('text: ' + text_body, flush=True)

    try:
        url = app.config.get('API_URL') or 'https://api.sendgrid.com/v3/mail/send'
        api_key = app.config.get('API_KEY')
        api_from = app.config.get('API_FROM')
        prefix = app.config.get('FLASKY_MAIL_SUBJECT_PREFIX')
        full_subject = f"{prefix} {subject}".strip() if prefix else subject

        is_sendgrid = 'sendgrid.com' in str(url) or (api_key and str(api_key).startswith('SG.'))

        if is_sendgrid:
            if isinstance(to, list):
                to_list = [{"email": addr} for addr in to]
            else:
                to_list = [{"email": to}]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "personalizations": [
                    {
                        "to": to_list
                    }
                ],
                "from": {
                    "email": api_from
                },
                "subject": full_subject,
                "content": [
                    {
                        "type": "text/plain",
                        "value": text_body
                    }
                ]
            }
            resposta = requests.post(url, headers=headers, json=payload)
        else:
            resposta = requests.post(url, 
                                     auth=("api", api_key), 
                                     data={"from": api_from, 
                                           "to": to, 
                                           "subject": full_subject, 
                                           "text": text_body})
            
        print('Enviando mensagem (Resposta)...' + str(resposta) + ' - ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True)
        if hasattr(resposta, 'status_code') and resposta.status_code >= 400:
            print('Detalhes do erro:', resposta.status_code, resposta.text, flush=True)
        return resposta
    except Exception as e:
        print('Erro ao enviar mensagem:', e, flush=True)
        return None