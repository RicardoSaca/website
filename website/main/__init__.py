from flask import Blueprint, render_template, request, flash
from flask_mail import Message
from website import mail

from website.models import Book, Project
from website.forms import ContactForm

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    latest_projects = Project.query.filter(Project.pro_show.is_(True)).all()
    return render_template("home.html", latest_projects=latest_projects)

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
            except:
                import sys
                e = sys.exc_info()[0]
                print("error! email failed to send")
                print(e)
                return render_template('error.html')

    elif request.method == 'GET':
        return  render_template('contact.html', form=form)

@main.route('/portfolio')
def portfolio():
    projects = Project.query.order_by(Project.pro_date.desc()).all()
    return render_template("portfolio.html", projects=projects)

@main.route('/project/<projectid>')
def project(projectid):
    pro = Project.query.get(projectid)
    return render_template("project.html", pro=pro)

@main.route('/bookshelf')
def bookshelf():
    books = get_books()

    years = []
    for book in books:
        print(book.name, book.date_finished)
        if book.date_finished:
            years.append(book.date_finished.strftime('%Y'))
    years_set = set(years)
    # convert the set to the list
    years = (list(years_set))
    years.sort(reverse = True)
    return render_template("bookshelf.html", books=books, years=years)

@main.route('/comingsoon')
def comingsoon():
    return render_template("comingsoon.html")

@main.route('/error')
def error():
    return render_template("error.html")

def get_books():
    books = Book.query.order_by(Book.date_finished.desc()).all()
    return books
