from flask_mail import Mail
from configparser import ConfigParser
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

db = SQLAlchemy()
login = LoginManager()
admin = Admin()
mail = Mail()
config = ConfigParser()