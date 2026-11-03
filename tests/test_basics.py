import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_new_user_triggers_email(self):
        from unittest.mock import patch
        from app.models import User

        client = self.app.test_client()
        with patch('app.main.views.send_simple_message') as mock_send:
            response = client.post('/', data={'name': 'Aluno Teste'}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            user = User.query.filter_by(username='Aluno Teste').first()
            self.assertIsNotNone(user)
            self.assertTrue(mock_send.called)
            recipients, subject, user_input = mock_send.call_args[0]
            self.assertIn('flaskaulasweb@zohomail.com', recipients)
            self.assertEqual(user_input, 'Aluno Teste')

    def test_send_simple_message_format(self):
        from unittest.mock import patch
        from app.email import send_simple_message

        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 202
            send_simple_message(['flaskaulasweb@zohomail.com'], 'Novo usuário', 'Maria', user_email='maria@teste.com')
            self.assertTrue(mock_post.called)
            kwargs = mock_post.call_args[1]
            if 'json' in kwargs:
                payload = kwargs['json']
                content_text = payload['content'][0]['value']
                self.assertIn('Novo usuário cadastrado: Maria', content_text)
                self.assertIn('Email inputado: maria@teste.com', content_text)
                self.assertIn('Wellington Mendes', content_text)
                self.assertIn('PT303772X', content_text)
                self.assertIn('Bearer', kwargs['headers']['Authorization'])
                self.assertEqual(payload['personalizations'][0]['to'], [{'email': 'flaskaulasweb@zohomail.com'}])
            else:
                data = kwargs['data']
                self.assertIn('Novo usuário cadastrado: Maria', data['text'])
                self.assertIn('Email inputado: maria@teste.com', data['text'])
                self.assertIn('Wellington Mendes', data['text'])
                self.assertIn('PT303772X', data['text'])

    def test_new_user_with_custom_email_and_page_rendering(self):
        from unittest.mock import patch
        from app.models import User

        client = self.app.test_client()
        with patch('app.main.views.send_simple_message') as mock_send:
            response = client.post('/', data={
                'name': 'tom',
                'email': 'tom@example.com'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            user = User.query.filter_by(username='tom').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role.name, 'User')
            self.assertTrue(mock_send.called)
            recipients, _, user_input = mock_send.call_args[0]
            self.assertIn('tom@example.com', recipients)
            self.assertEqual(user_input, 'tom')
            self.assertEqual(mock_send.call_args.kwargs.get('user_email'), 'tom@example.com')

            html = response.get_data(as_text=True)
            self.assertIn('Avaliação contínua: <strong>Aula 080</strong>', html)
            self.assertIn('Olá, tom!', html)
            self.assertIn('Prazer em conhecê-lo!', html)
            self.assertIn('E-mail enviado para o Administrador do sistema, notificando o cadastro de um novo usuário.', html)
            self.assertIn('Qual é o seu email (Envio de notificação de novo usuário)?', html)
            self.assertIn('Relação de usuários cadastrados', html)
            self.assertIn('Nome do usuário', html)
            self.assertIn('Função', html)
            self.assertIn('tom', html)
            self.assertIn('Editar', html)
            self.assertIn('Excluir', html)
            self.assertIn(f'/edit/{user.id}', html)
            self.assertIn(f'/delete/{user.id}', html)

    def test_edit_user(self):
        from app.models import User, Role

        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User')
            db.session.add(user_role)
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin')
            db.session.add(admin_role)
        user = User(username='Ciclano', role=user_role)
        db.session.add(user)
        db.session.commit()

        client = self.app.test_client()
        # Test GET edit
        get_res = client.get(f'/edit/{user.id}')
        self.assertEqual(get_res.status_code, 200)
        self.assertIn('Edição de Usuário', get_res.get_data(as_text=True))
        self.assertIn('Ciclano', get_res.get_data(as_text=True))

        # Test POST edit
        post_res = client.post(f'/edit/{user.id}', data={
            'name': 'Ciclano Silva',
            'role': 'Admin'
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)

        updated_user = db.session.get(User, user.id)
        self.assertEqual(updated_user.username, 'Ciclano Silva')
        self.assertEqual(updated_user.role.name, 'Admin')

    def test_delete_user(self):
        from app.models import User, Role

        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User')
            db.session.add(user_role)
        user = User(username='ParaExcluir', role=user_role)
        db.session.add(user)
        db.session.commit()

        user_id = user.id
        client = self.app.test_client()
        res = client.get(f'/delete/{user_id}', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        deleted = db.session.get(User, user_id)
        self.assertIsNone(deleted)
