from flask import Flask, redirect, url_for
from flask_mail import Mail
from configparser import ConfigParser
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from config import Config

db = SQLAlchemy()
login = LoginManager()
admin = Admin()
mail = Mail()
config = ConfigParser()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    app.config.update(Config.mail_settings)

    #init db
    db.init_app(app)

    #init login manager
    login.init_app(app)
    login.login_view = 'login'

    from website.models import Book, Project, User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # init admin
    class MyModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('main.home'))

    class MyAdminIndexView(AdminIndexView):
        def is_accessible(self):
            return current_user.is_authenticated

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('main.home'))

    #Initialize FLASK-Admin and Database
    admin.init_app(app, index_view=MyAdminIndexView())

    #Set Views for FLASK-Admin
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Project, db.session))
    admin.add_view(MyModelView(Book, db.session))

    # register blueprints
    from website.main import main
    app.register_blueprint(main)
    from website.auth import auth
    app.register_blueprint(auth)

    return app