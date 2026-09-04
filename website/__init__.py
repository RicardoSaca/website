from flask import Flask, redirect, url_for
# from flask_mail import Mail
# from configparser import ConfigParser
# from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_admin import AdminIndexView
from wtforms import SelectField
from flask_admin.form import Select2Widget
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import event
from config import Config
from markupsafe import Markup
from datetime import datetime, timezone
from .models import fetch_cover_from_openlibrary

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
        column_list = ['cover_thumb','title', 'author', 'progress','started_at','date_finished','duration', 'notes', 'isbn', 'created_at']
        column_filters = ['title', 'author', 'progress']
        column_formatters = {
            'duration': lambda v, c, m, p: f'{m.duration.days} days' if m.duration else None,
            'cover_thumb': lambda v, c, model, n: Markup(
                f'<img src="/book/{model.id}/cover" style="max-height:60px">'
            ) if model.cover_image else 'No cover'
        }
        form_columns = ['title', 'author','isbn', 'started_at','date_finished', 'progress', 'notes', 'created_at']
        form_overrides = {
            'progress': SelectField
        }
        # form_excluded_columns = ('cover_image', 'cover_mimetype', 'cover_fetched_at')
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
        @action('refetch_cover', 'Re-fetch cover', 'Re-fetch covers for selected books?')
        def action_refetch_cover(self, ids):
            books = Book.query.filter(Book.id.in_(ids)).all()
            for book in books:
                content, mimetype = fetch_cover_from_openlibrary(book.isbn)
                if content:
                    book.cover_image = content
                    book.cover_mimetype = mimetype
                    book.cover_fetched_at = datetime.now(timezone.utc)
            db.session.commit()

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