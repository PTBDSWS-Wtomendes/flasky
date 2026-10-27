import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.zoho.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'flaskaulas@zohomail.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_API_URL = os.environ.get('SENDGRID_API_URL', 'https://api.sendgrid.com/v3/mail/send')
    SENDGRID_FROM = os.environ.get('SENDGRID_FROM')

    API_KEY = os.environ.get('SENDGRID_API_KEY') or os.environ.get('API_KEY') or os.environ.get('MAILGUN_API_KEY')
    API_URL = os.environ.get('SENDGRID_API_URL') or os.environ.get('API_URL') or os.environ.get('MAILGUN_API_URL') or 'https://api.sendgrid.com/v3/mail/send'
    API_FROM = os.environ.get('SENDGRID_FROM') or os.environ.get('API_FROM') or os.environ.get('MAILGUN_FROM')
    STUDENT_NAME = os.environ.get('STUDENT_NAME', 'Wellington Mendes')
    STUDENT_PRONTUARIO = os.environ.get('STUDENT_PRONTUARIO', 'PT303772X')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}