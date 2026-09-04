from flask import Blueprint,Response, render_template, request, flash, send_from_directory, redirect, url_for, abort
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from website.extensions import mail
import json
import plotly
import os
import re
import traceback
import html
from website.models import Book, Project
from website.forms import ContactForm
from website.animation import get_books_df, book_animation, save_file
from website.visualization import draw_book_viz

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    latest_projects = get_latest_projects(3)
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


@main.route('/book/<int:book_id>/cover')
def book_cover(book_id):
    book = Book.query.get_or_404(book_id)
    if book.cover_image:
        resp = Response(book.cover_image, mimetype=book.cover_mimetype or 'image/jpeg')
    else:
        resp = Response(generate_placeholder_cover(book.title, book.author), mimetype='image/svg+xml')
    resp.headers['Cache-Control'] = 'public, max-age=604800'
    return resp

@main.route('/bookshelf')
def bookshelf():
    books = get_books()
    wish_books = [book for book in books if book.progress == 'Wish']
    other_books = [book for book in books if book.progress != 'Wish']

    # Sort wish_books by author and then by title
    wish_books_sorted = sorted(wish_books, key=lambda x: (x.author, get_series_number(x.title), x.title))

    # Combine the sorted lists
    sorted_books = wish_books_sorted + other_books

    years = get_years(books)
    return render_template("bookshelf.html", books=sorted_books, years=years)

@main.route('/bookshelf_analytics')
def analytics():
    books_df = get_books_df()
    fig = draw_book_viz(books_df)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("analytics.html", graphJSON=graphJSON)

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

def get_series_number(title):
    match = re.search(r'\b(\d+)\)', title)
    return int(match.group(1)) if match else float('inf')

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

def get_latest_projects(num):
    latest_projects = Project.query.filter(Project.pro_show.is_(True)).order_by(Project.pro_date.desc()).limit(num)
    return latest_projects

def get_project(projectid):
    pro = Project.query.get(projectid)
    return pro

def generate_placeholder_cover(title, author, width=200, height=300):
    title = html.escape(title or "Untitled")
    author = html.escape(author or "Unknown")

    def wrap(text, max_chars=18):
        words = text.split()
        lines, current = [], ""
        for w in words:
            if len(current) + len(w) + 1 <= max_chars:
                current = f"{current} {w}".strip()
            else:
                lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines[:4]  # cap so long titles don't overflow

    title_lines = wrap(title)
    tspans = "".join(
        f'<tspan x="50%" dy="{"0" if i == 0 else "1.2em"}">{line}</tspan>'
        for i, line in enumerate(title_lines)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#6c757d"/>
  <text x="50%" y="42%" text-anchor="middle" fill="white" font-family="sans-serif" font-size="16" font-weight="bold">{tspans}</text>
  <text x="50%" y="88%" text-anchor="middle" fill="#e9ecef" font-family="sans-serif" font-size="12">{author}</text>
</svg>'''