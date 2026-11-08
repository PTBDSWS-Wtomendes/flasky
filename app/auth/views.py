from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, Role
from ..email import send_email
from .forms import (
    LoginForm, RegistrationForm, ChangePasswordForm,
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
            password=form.password.data
        )
        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User')
            db.session.add(user_role)
        user.role = user_role
        db.session.add(user)
        db.session.commit()
        flash('You can now log in.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            if current_user.email:
                send_email(
                    current_user.email,
                    'Confirmação: Senha Alterada',
                    'auth/email/password_changed',
                    user=current_user
                )
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                'Redefinição de Senha',
                'auth/email/reset_password',
                user=user,
                token=token
            )
            flash('An email with instructions to reset your password has been sent to you.')
            reset_url = url_for('auth.password_reset', token=token, _external=True)
            flash(f'To reset your password <a href="{reset_url}">click here</a>')
            return redirect(url_for('auth.login'))
        flash('Unknown email address.')
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.reset_password(token, form.password.data)
        if user:
            if user.email:
                send_email(
                    user.email,
                    'Confirmação: Senha Alterada',
                    'auth/email/password_changed',
                    user=user
                )
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            flash('The password reset link is invalid or has expired.')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(
                new_email,
                'Confirmação de Novo Endereço de E-mail',
                'auth/email/change_email',
                user=current_user,
                token=token
            )
            flash('An email with instructions to confirm your new email address has been sent to you.')
            confirm_url = url_for('auth.change_email', token=token, _external=True)
            flash(f'To confirm your new email address <a href="{confirm_url}">click here</a>')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    old_email = current_user.email
    if current_user.change_email(token):
        if old_email:
            send_email(
                old_email,
                'Notificação: Endereço de E-mail Alterado',
                'auth/email/email_changed',
                user=current_user,
                new_email=current_user.email
            )
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
