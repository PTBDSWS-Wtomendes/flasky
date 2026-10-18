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
            mock_post.return_value.status_code = 200
            send_simple_message(['flaskaulasweb@zohomail.com'], 'Novo usuário', 'Maria')
            self.assertTrue(mock_post.called)
            data = mock_post.call_args[1]['data']
            self.assertIn('Novo usuário cadastrado: Maria', data['text'])
            self.assertIn('Wellington Mendes', data['text'])
            self.assertIn('PT303772X', data['text'])
