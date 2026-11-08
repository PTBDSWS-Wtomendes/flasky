from urllib.parse import urljoin, urlsplit

from flask import current_app, render_template, url_for
from flask_mail import Message
import requests
from . import mail


def _recipients(to):
    return [to] if isinstance(to, str) else list(to)


def _public_url(endpoint, **values):
    """Create links using the public site URL when it is configured."""
    external_url = url_for(endpoint, _external=True, **values)
    base_url = current_app.config.get('APP_BASE_URL')
    if not base_url:
        return external_url

    parts = urlsplit(external_url)
    path = parts.path + (f'?{parts.query}' if parts.query else '')
    return urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))


def _send(app, to, subject, text_body, html_body):
    """Deliver an email and return whether the provider accepted it."""
    prefix = app.config.get('FLASKY_MAIL_SUBJECT_PREFIX', '')
    full_subject = f'{prefix} {subject}'.strip() if prefix else subject
    api_key = app.config.get('SENDGRID_API_KEY') or app.config.get('API_KEY')
    api_from = (app.config.get('SENDGRID_FROM') or app.config.get('API_FROM') or
                app.config.get('FLASKY_MAIL_SENDER'))
    api_from_name = app.config.get('SENDGRID_FROM_NAME')
    url = app.config.get('SENDGRID_API_URL') or app.config.get('API_URL')

    if api_key and api_from and url and 'sendgrid.com' in url:
        payload = {
            'personalizations': [{'to': [{'email': address} for address in _recipients(to)]}],
            'from': {'email': api_from, 'name': api_from_name},
            'reply_to': {'email': api_from, 'name': api_from_name},
            'subject': full_subject,
            'content': [item for item in (
                {'type': 'text/plain', 'value': text_body} if text_body else None,
                {'type': 'text/html', 'value': html_body} if html_body else None,
            ) if item],
        }
        try:
            response = requests.post(
                url, headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json=payload, timeout=10)
            response.raise_for_status()
            app.logger.info('Email accepted by SendGrid for %s.', ', '.join(_recipients(to)))
            return True
        except requests.RequestException:
            app.logger.exception('SendGrid rejected or could not receive email for %s.', ', '.join(_recipients(to)))
            return False

    if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
        try:
            message = Message(full_subject, sender=api_from, recipients=_recipients(to))
            message.body, message.html = text_body, html_body
            mail.send(message)
            app.logger.info('Email accepted by SMTP for %s.', ', '.join(_recipients(to)))
            return True
        except Exception:
            app.logger.exception('SMTP could not send email for %s.', ', '.join(_recipients(to)))
            return False

    app.logger.error('Email was not sent: no email provider is configured.')
    return False


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()

    kwargs['public_url'] = _public_url
    text_body = render_template(template + '.txt', **kwargs)
    html_body = render_template(template + '.html', **kwargs)
    return _send(app, to, subject, text_body, html_body)


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
