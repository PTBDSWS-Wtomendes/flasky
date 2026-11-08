from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
import requests
from datetime import datetime


def send_async_email(app, to, subject, text_body, html_body):
    with app.app_context():
        _send(app, to, subject, text_body, html_body)


def _send(app, to, subject, text_body, html_body):
    prefix = app.config.get('FLASKY_MAIL_SUBJECT_PREFIX', '')
    full_subject = f"{prefix} {subject}".strip() if prefix else subject
    url = app.config.get('SENDGRID_API_URL') or app.config.get('API_URL') or 'https://api.sendgrid.com/v3/mail/send'
    api_key = app.config.get('SENDGRID_API_KEY') or app.config.get('API_KEY')
    api_from = app.config.get('SENDGRID_FROM') or app.config.get('API_FROM') or app.config.get('FLASKY_MAIL_SENDER', 'flaskaulas@zohomail.com')

    is_sendgrid = (api_key and str(api_key).startswith('SG.')) or ('sendgrid.com' in str(url))

    if is_sendgrid and api_key and api_from:
        try:
            if isinstance(to, list):
                to_list = [{"email": addr} for addr in to]
            else:
                to_list = [{"email": to}]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            content_items = []
            if text_body:
                content_items.append({"type": "text/plain", "value": text_body})
            if html_body:
                content_items.append({"type": "text/html", "value": html_body})
            if not content_items:
                content_items.append({"type": "text/plain", "value": full_subject})

            payload = {
                "personalizations": [{"to": to_list}],
                "from": {"email": api_from},
                "subject": full_subject,
                "content": content_items
            }
            res = requests.post(url, headers=headers, json=payload)
            print(f"Email sent via SendGrid to {to}: {res.status_code}", flush=True)
            return res
        except Exception as e:
            print('Erro ao enviar mensagem via SendGrid:', e, flush=True)

    # Fallback to Flask-Mail if configured
    try:
        msg = Message(full_subject, sender=api_from, recipients=[to] if isinstance(to, str) else to)
        if text_body:
            msg.body = text_body
        if html_body:
            msg.html = html_body
        mail.send(msg)
        print(f"Email sent via Flask-Mail to {to}", flush=True)
    except Exception as e:
        print('Erro ao enviar mensagem via Flask-Mail:', e, flush=True)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()

    text_body = None
    html_body = None
    try:
        text_body = render_template(template + '.txt', **kwargs)
    except Exception:
        pass
    try:
        html_body = render_template(template + '.html', **kwargs)
    except Exception:
        pass
    if not text_body and not html_body:
        text_body = subject

    if app.config.get('TESTING'):
        _send(app, to, subject, text_body, html_body)
        return None

    thr = Thread(target=send_async_email, args=[app, to, subject, text_body, html_body])
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
    return _send(app, to, subject, text_body, None)
