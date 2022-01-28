import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'there-is-no-spoon'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://lewkis:123456@localhost/weborders'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 25
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'gw-office'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'borovikao'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '978388'
    ADMINS = ['it@soveren.ru']
    FILE_TYPE_EXP = [(1, "dbf"), (2, "txt")]

