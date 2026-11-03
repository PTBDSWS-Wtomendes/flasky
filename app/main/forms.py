from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from werkzeug.datastructures import ImmutableMultiDict
from ..models import Role
from .. import db


class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    email = StringField('Qual é o seu email (Envio de notificação de novo usuário)?')
    submit = SubmitField('Submit')


class EditUserForm(FlaskForm):
    name = StringField('Nome do usuário', validators=[DataRequired()])
    role = SelectField('Função', validators=[DataRequired()])
    submit = SubmitField('Salvar')

    def __init__(self, *args, **kwargs):
        roles = Role.query.all()
        if not roles:
            roles = [Role(name='User'), Role(name='Admin')]
            db.session.add_all(roles)
            db.session.commit()

        id_to_name = {str(r.id): r.name for r in roles}
        if not args and not kwargs.get('formdata'):
            if request and request.method in ('POST', 'PUT', 'PATCH') and request.form:
                d = request.form.to_dict(flat=False)
                modified = False
                if 'username' in d and 'name' not in d:
                    d['name'] = d['username']
                    modified = True
                if 'role' in d and d['role'] and d['role'][0] in id_to_name:
                    d['role'] = [id_to_name[d['role'][0]]]
                    modified = True
                if modified:
                    kwargs['formdata'] = ImmutableMultiDict(d)

        super(EditUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(r.name, r.name) for r in roles]

    @property
    def username(self):
        return self.name

    @username.setter
    def username(self, val):
        self.name = val


UserForm = EditUserForm
EditForm = EditUserForm
