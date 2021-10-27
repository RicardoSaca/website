from flask import Blueprint, render_template, request, flash, send_from_directory, current_app
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from website.extensions import mail
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import os
import traceback
import pandas as pd

from website.models import Book, Project
from website.forms import ContactForm

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
    with current_app.app_context():
        con = current_app.config['SQLALCHEMY_DATABASE_URI']
        query = pd.read_sql_query("SELECT * FROM Books ORDER BY date_finished ASC;", con=con)
        html = book_animation(query)
    return render_template("bookshelf_analytics.html", html=html)

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
    print(books)
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

def book_animation(df):
    plt.switch_backend('Agg')
    df['date_finished'] = pd.to_datetime(df['date_finished'])
    df['year'] = df['date_finished'].dt.year
    pd.options.display.float_format = '{:.0f}'.format

    #Set dateformat
    dateformat='%b/%y'
    #Change date format from data to correct one
    df['monthYear'] = df['date_finished'].dt.strftime(dateformat)
    #Group data by monthYear
    sumMonthYear = df.groupby('monthYear')['title'].count()
    sumMonthYear.to_frame().reset_index()
    #Get starting data and ending date
    startYear = min(df['date_finished'])
    startYear = startYear - pd.offsets.DateOffset(months=1)
    endYear = max(df['date_finished'])
    #Off set date by one month
    yearList = pd.date_range(startYear, endYear, freq='MS').strftime(dateformat).tolist()
    #Data frame of each month of interest
    numBooks = pd.DataFrame()
    numBooks['monthYear'] = yearList
    numBooks['count']=0
    #Merge numBooks with sumMonthYear
    booksTotal = pd.merge(numBooks, sumMonthYear, how='outer', on='monthYear')
    #Drop count and replace NaN with 0
    booksTotal.drop(columns=['count'], inplace=True)
    booksTotal.fillna(0, inplace=True)
    #make monthYear datetime
    numBooks['monthYear'] = pd.to_datetime(numBooks.monthYear, errors='coerce').dt.strftime('%b/%y')
    #Add a running total and difference column
    booksTotal['total'] = booksTotal.title.cumsum()
    booksTotal['diff'] = booksTotal.total.diff()
    booksTotal.fillna(0, inplace=True)

    plt.rcParams['animation.html'] = 'jshtml'

    #Set values for charting
    dates = pd.to_datetime(booksTotal.monthYear.values, format='%b/%y')
    x = dates
    y = booksTotal.total.values

    #Initialize plot
    fig, (ax1, ax2) = plt.subplots(1, 2,gridspec_kw={'width_ratios': [2,1]},
                                    figsize=(12,6), dpi=600)

    #Update ticks
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.set_xticks(dates)
    fmt_month = mdates.MonthLocator(interval=2)
    ax1.xaxis.set_major_locator(fmt_month)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b/%y'))
    ax1.format_xdata = mdates.DateFormatter('%b/%y')
    fig.autofmt_xdate()

    #Set chart axis limits
    xlim = (dates.min(), dates.max())
    ylim = (booksTotal.total.min(), booksTotal.total.max()+5)
    ax1.set(xlim=xlim, ylim=ylim)

    #Customize plot spines
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    #initialize plot line
    l, = ax1.plot([],[])

    #initalize annotation
    tally = ax1.annotate('', xy=(1,0),
        textcoords="offset points", ha='center'
    )
    running = ax1.text(0.01, 0.93,'',
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform = ax1.transAxes)

    #Set plot Title
    fig.suptitle("Books Read through the Years", fontsize=15)

    def animate(i, x, y, l):
        l.set_data(x[:i], y[:i])
        j = i-1
        if i == 0:
            running.set_text(f'Books finished on {x[i]:%b-%y} :{0}')
        else:
            running.set_text(f'Books finished on {x[j]:%b-%y} : {"+" if booksTotal["diff"][j] != 0 else ""}{booksTotal["diff"][j]:.0f}')
            tally.set_text(f'{y[j]:.0f}')
            tally.xy = (x[j],y[j]+1)
        return l, tally, running

    #Bar Plot
    counts = df["year"].value_counts()
    ax2.bar(counts.index, counts.values)

    #Annotate bar plot
    for p in ax2.patches:
        ax2.annotate("{:.0f}".format(p.get_height()),
                    (p.get_x()+ p.get_width() /2, p.get_height()-.1),
                    ha='center',va='center', xytext=(0,8),
                    textcoords='offset points')

    #Set bar plot labels
    ax2.set_xticks(counts.index.tolist())
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")

    #Set goal of 2021 at 12 books
    ax2.axhline(y=12, color='black', linestyle='--', label='Goal for 2021')
    ax2.text(0.02, ((1/counts.iloc[0])*12),'Goal for 2021',
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform = ax2.transAxes)
    #Customize bar plot spines
    ax2.spines['left'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    #Customize figure color
    plt.figure(facecolor='white')

    #Animate Plot
    animation = FuncAnimation(fig, func=animate, frames=booksTotal.shape[0],interval=550, fargs=[x,y,l], blit=True)

    # f = r"/Users/ricardosaca/Documents/projects/bookanalytics/final.mp4"
    # writervideo = FFMpegWriter(fps=5, bitrate=600)
    # animation.save(f, writer=writervideo, dpi=600)
    # #Save Plot
    html = animation.to_html5_video()
    html = html.replace('width="7200" height="3600"','width="900" height="450"')
    print(html[:50])

    return html


