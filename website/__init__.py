from flask import Flask, redirect, url_for
# from flask_mail import Mail
# from configparser import ConfigParser
# from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_admin import AdminIndexView
from wtforms import SelectField
from flask_admin.form import Select2Widget
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import event
from config import Config


def create_app():
    app = Flask(__name__)

    #import extensions
    from website.extensions import db, login, admin, mail, config, migrate

    app.config.from_object(Config)
    app.config.update(Config.mail_settings)

    #init db
    db.init_app(app)

    # add migratrion
    migrate.init_app(app, db)

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

    class BookModelView(MyModelView):
        column_searchable_list = ['title', 'author', 'progress']
        column_list = ['title', 'author', 'progress','started_at','date_finished','duration', 'notes', 'isbn', 'created_at']
        column_filters = ['title', 'author', 'progress']
        column_formatters = {
            'duration': lambda v, c, m, p: f'{m.duration.days} days' if m.duration else None
        }
        form_columns = ['title', 'author','isbn', 'started_at','date_finished', 'progress', 'notes', 'created_at']
        form_overrides = {
            'progress': SelectField
        }
        form_args = {
            'progress': {
                'choices': [
                    ('Wish', 'Wishlist'),
                    ('Progress', 'Progress'),
                    ('Read', 'Read'),
                    ('Favorite', 'Favorite')
                ],
                'widget': Select2Widget()
            }
        }

    #Initialize FLASK-Admin and Database
    admin.init_app(app, index_view=MyAdminIndexView())

    #Set Views for FLASK-Admin
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Project, db.session))
    admin.add_view(BookModelView(Book, db.session))

    #init mail
    mail.init_app(app)

    # register blueprints
    with app.app_context():
        from website.main import main
        app.register_blueprint(main)
        from website.auth import auth
        app.register_blueprint(auth)

    return app