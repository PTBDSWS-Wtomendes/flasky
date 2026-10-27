from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User, Role
from ..email import send_email, send_simple_message
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name='User').first()
            if not user_role:
                user_role = Role(name='User')
                db.session.add(user_role)
                db.session.commit()
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            print('FLASKY_ADMIN: ' + str(current_app.config['FLASKY_ADMIN']), flush=True)
            if current_app.config.get('FLASKY_ADMIN'):
                print('Enviando mensagem...', flush=True)
                raw_admins = current_app.config['FLASKY_ADMIN']
                if isinstance(raw_admins, list):
                    admins = raw_admins
                else:
                    admins = [e.strip() for e in str(raw_admins).split(',') if e.strip()]
                recipients = list(dict.fromkeys(admins + ["flaskaulasweb@zohomail.com"]))
                user_email = form.email.data.strip() if form.email.data and form.email.data.strip() else None
                if user_email and user_email not in recipients:
                    recipients.append(user_email)
                send_simple_message(recipients, 'Novo usuário', form.name.data, user_email=user_email)
                print('Mensagem enviada...', flush=True)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           users=User.query.all())

