from flask import render_template, session, redirect, url_for, current_app, flash, request
from .. import db
from ..models import User, Role
from ..email import send_email, send_simple_message
from . import main
from .forms import NameForm, EditUserForm, UserForm


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


@main.route('/user/<int:id>/edit', methods=['GET', 'POST'], endpoint='user_id_edit')
@main.route('/user/edit/<int:id>', methods=['GET', 'POST'], endpoint='user_edit')
@main.route('/edit_user/<int:id>', methods=['GET', 'POST'], endpoint='edit_user_alt')
@main.route('/edit/<int:id>', methods=['GET', 'POST'], endpoint='edit')
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = EditUserForm()
    if form.validate_on_submit():
        new_username = form.name.data.strip()
        user.username = new_username
        if form.role.data:
            role = Role.query.filter_by(name=form.role.data).first()
            if not role and form.role.data.isdigit():
                role = db.session.get(Role, int(form.role.data))
            if role:
                user.role = role
        db.session.add(user)
        db.session.commit()
        if session.get('name') and session.get('name') != new_username:
            session['name'] = new_username
        flash('Usuário atualizado com sucesso!')
        return redirect(url_for('.index'))
    form.name.data = user.username
    if user.role:
        form.role.data = user.role.name
    return render_template('edit_user.html', form=form, user=user)


@main.route('/user/<int:id>/delete', methods=['GET', 'POST'], endpoint='user_id_delete')
@main.route('/user/delete/<int:id>', methods=['GET', 'POST'], endpoint='user_delete')
@main.route('/delete_user/<int:id>', methods=['GET', 'POST'], endpoint='delete_user_alt')
@main.route('/delete/<int:id>', methods=['GET', 'POST'], endpoint='delete')
@main.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    user = User.query.filter_by(id=id).first_or_404()
    if session.get('name') == user.username:
        session.pop('name', None)
        session.pop('known', None)
    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso!')
    return redirect(url_for('.index'))
