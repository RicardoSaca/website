import os

class Config(object):
    uri = os.environ.get("DATABASE_URL")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('secret_key')
    MAIL_USER = os.environ.get('EMAIL_USERNAME')
    PASSWORD = os.environ.get('EMAIL_PASSWORD')
    mail_settings ={
    "MAIL_SERVER" : "smtp.gmail.com",
    "MAIL_PORT" : 465,
    "MAIL_USERNAME" : MAIL_USER,
    "MAIL_PASSWORD" : PASSWORD,
    "MAIL_USE_TLS" : False,
    "MAIL_USE_SSL" : True,
    }