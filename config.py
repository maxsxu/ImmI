# coding=utf-8

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <admin@immi.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME=0.5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    # MySQL SETTINGS
    mysql_db_username = 'root'
    mysql_db_password = ''
    mysql_db_name = 'immi'
    mysql_db_hostname = 'localhost'

    HOST = "127.0.0.1"
    PORT = 5002
    SQLALCHEMY_ECHO = False
    SECRET_KEY = "IMMI TOP SECRET"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=mysql_db_username,
                                                                                               DB_PASS=mysql_db_password,
                                                                                               DB_ADDR=mysql_db_hostname,
                                                                                               DB_NAME=mysql_db_name)
    # Email Server Configuration
    MAIL_DEFAULT_SENDER = "immi@localhost"

    PASSWORD_RESET_EMAIL = """
        Hi,

          Please click on the link below to reset your password

          <a href="/forgotpassword/{token}> Click here </a>
    """

config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}

if __name__ == '__main__':
    pass
