from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from website.extensions import login, db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(50))
    date_finished = db.Column(db.Date)
    progress = db.Column(db.String(10))
    blog_url = db.Column(db.String(200))
    notes = db.Column(db.Text)
    isbn = db.Column(db.Text(10))

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    pro_name = db.Column(db.String(50))
    pro_author = db.Column(db.String(30))
    pro_date = db.Column(db.Date)
    pro_desc = db.Column(db.Text)
    pro_link = db.Column(db.Text)
    pro_embed = db.Column(db.Text)
    pro_show = db.Column(db.Boolean, unique=False, default=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))