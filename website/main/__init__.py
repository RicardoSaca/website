from flask import Blueprint, render_template, request, flash, send_from_directory, redirect, url_for
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from website.extensions import mail
import os
import traceback
from website.models import Book, Project
from website.forms import ContactForm
from website.animation import get_books_df, book_animation, save_file

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    latest_projects = get_latest_projects()
    latest_books = get_latest_books(3)
    return render_template("home.html", latest_projects=latest_projects, latest_books=latest_books)

@main.route('/about')
def about():
    return render_template("about.html")

@main.route('/contactme', methods=['GET','POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required')
            return render_template('contact.html', form=form)
        else:
            try:
                    msg = Message(f'Message from {form.name.data}', sender='ricardosaca98@gmail.com', recipients=['ricardosaca@gmail.com'])
                    msg.body = """
                    %s has contacted you.
                    You can reply to this email address <%s>
                    They said:

                    %s

                    """ % (form.name.data, form.email.data, form.message.data)
                    mail.send(msg)
                    print("success! email sent")
                    return render_template('contact.html', success=True)
            except Exception:
                import sys
                e = sys.exc_info()[0]
                print("error! email failed to send")
                print(e, sys.exc_info()[2])
                print(traceback.format_exc())
                return render_template('error.html')

    elif request.method == 'GET':
        return  render_template('contact.html', form=form)

@main.route('/portfolio')
def portfolio():
    projects = get_projects()
    return render_template("portfolio.html", projects=projects)

@main.route('/project/<projectid>')
def project(projectid):
    pro = get_project(projectid)
    return render_template("project.html", pro=pro)

@main.route('/bookshelf')
def bookshelf():
    books = get_books()
    years = get_years(books)
    return render_template("bookshelf.html", books=books, years=years)

@main.route('/bookshelf_analytics')
def analytics():
    return render_template("analytics.html")

@main.route('/set_analytics')
def set_analytics():
    save_file(book_animation(get_books_df()))
    return redirect(url_for('main.analytics'))

@main.route('/comingsoon')
def comingsoon():
    return render_template("comingsoon.html")

@main.route('/error')
def error():
    return render_template("error.html")

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

######  Helper formulas ######
def get_books():
    books = Book.query.order_by(Book.date_finished.desc()).all()
    return books

def get_years(books):
    years = []
    for book in books:
        if book.date_finished:
            years.append(book.date_finished.strftime('%Y'))
    years_set = set(years)
    # convert the set to the list
    years = (list(years_set))
    years.sort(reverse = True)
    return years

def get_latest_books(num):
    books = Book.query.filter(Book.date_finished.is_not(None)).order_by(Book.date_finished.desc()).limit(num)
    return books

def get_projects():
    projects = Project.query.order_by(Project.pro_date.desc()).all()
    return projects

def get_latest_projects():
    latest_projects = Project.query.filter(Project.pro_show.is_(True)).order_by(Project.pro_date.desc()).all()
    return latest_projects

def get_project(projectid):
    pro = Project.query.get(projectid)
    return pro

