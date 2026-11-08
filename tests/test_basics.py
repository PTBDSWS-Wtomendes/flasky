import unittest
from unittest.mock import patch
from flask import current_app
from app import create_app, db
from app.models import User, Role


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

    def test_anonymous_home_page(self):
        client = self.app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Flasky', html)
        self.assertIn('Hello, Stranger!', html)
        self.assertIn('Log In', html)
        self.assertNotIn('Account', html)

    def test_password_setter_and_verification(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
        with self.assertRaises(AttributeError):
            _ = u.password

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_registration_and_login(self):
        client = self.app.test_client()
        # Register user
        reg_response = client.post('/auth/register', data={
            'email': 'wtomendes@example.com',
            'username': 'wtomendes',
            'password': 'secretpassword',
            'password2': 'secretpassword'
        }, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn('You can now log in.', reg_response.get_data(as_text=True))

        user = User.query.filter_by(email='wtomendes@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'wtomendes')

        # Log in
        login_response = client.post('/auth/login', data={
            'email': 'wtomendes@example.com',
            'password': 'secretpassword'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        login_html = login_response.get_data(as_text=True)
        self.assertIn('Hello, wtomendes!', login_html)
        self.assertIn('Account', login_html)
        self.assertIn('Change Password', login_html)
        self.assertIn('Change Email', login_html)
        self.assertIn('Log Out', login_html)

        # Log out
        logout_response = client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(logout_response.status_code, 200)
        logout_html = logout_response.get_data(as_text=True)
        self.assertIn('Hello, Stranger!', logout_html)
        self.assertIn('You have been logged out.', logout_html)

    def test_password_reset_flow(self):
        user = User(email='user@example.com', username='testuser', password='oldpassword')
        db.session.add(user)
        db.session.commit()

        client = self.app.test_client()
        with patch('app.auth.views.send_email') as mock_send:
            # Request password reset
            req_res = client.post('/auth/reset', data={
                'email': 'user@example.com'
            }, follow_redirects=True)
            self.assertEqual(req_res.status_code, 200)
            req_html = req_res.get_data(as_text=True)
            self.assertIn('An email with instructions to reset your password has been sent to you.', req_html)
            self.assertIn('To reset your password', req_html)
            self.assertTrue(mock_send.called)

            token = mock_send.call_args.kwargs['token']
            self.assertIsNotNone(token)

            # Perform reset
            reset_res = client.post(f'/auth/reset/{token}', data={
                'password': 'newsecretpassword',
                'password2': 'newsecretpassword'
            }, follow_redirects=True)
            self.assertEqual(reset_res.status_code, 200)
            self.assertIn('Your password has been updated.', reset_res.get_data(as_text=True))

            # Verify password was updated
            updated_user = User.query.filter_by(email='user@example.com').first()
            self.assertTrue(updated_user.verify_password('newsecretpassword'))

    def test_change_password_flow(self):
        user = User(email='user2@example.com', username='user2', password='firstpassword')
        db.session.add(user)
        db.session.commit()

        client = self.app.test_client()
        # Log in
        client.post('/auth/login', data={
            'email': 'user2@example.com',
            'password': 'firstpassword'
        }, follow_redirects=True)

        with patch('app.auth.views.send_email') as mock_send:
            res = client.post('/auth/change-password', data={
                'old_password': 'firstpassword',
                'password': 'secondpassword',
                'password2': 'secondpassword'
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Your password has been updated.', res.get_data(as_text=True))
            self.assertTrue(mock_send.called)
            self.assertEqual(mock_send.call_args[0][0], 'user2@example.com')

            updated_user = User.query.filter_by(email='user2@example.com').first()
            self.assertTrue(updated_user.verify_password('secondpassword'))

    def test_change_email_flow(self):
        user = User(email='old@example.com', username='user3', password='password123')
        db.session.add(user)
        db.session.commit()

        client = self.app.test_client()
        client.post('/auth/login', data={
            'email': 'old@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        with patch('app.auth.views.send_email') as mock_send:
            res = client.post('/auth/change_email', data={
                'email': 'new@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('An email with instructions to confirm your new email address has been sent to you.', res.get_data(as_text=True))
            self.assertTrue(mock_send.called)
            token = mock_send.call_args.kwargs['token']

            # Confirm email change
            confirm_res = client.get(f'/auth/change_email/{token}', follow_redirects=True)
            self.assertEqual(confirm_res.status_code, 200)
            self.assertIn('Your email address has been updated.', confirm_res.get_data(as_text=True))

            updated_user = User.query.filter_by(username='user3').first()
            self.assertEqual(updated_user.email, 'new@example.com')
