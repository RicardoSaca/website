from flask import current_app
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation, FFMpegWriter

def get_books_df():
    with current_app.app_context():
        con = current_app.config['SQLALCHEMY_DATABASE_URI']
        query = pd.read_sql_query("SELECT id, title, author, date_finished FROM books WHERE books.date_finished IS NOT NULL ORDER BY books.date_finished ASC;", con=con)
        return query

def book_animation(df):
    plt.switch_backend('Agg')
    df['date_finished'] = pd.to_datetime(df['date_finished'])
    df['year'] = df['date_finished'].dt.year
    #Set dateformat
    dateformat='%b/%y'
    #Change date format from data to correct one
    df['monthYear'] = df['date_finished'].dt.strftime(dateformat)
    #Group data by monthYear
    sumMonthYear = df.groupby('monthYear')['title'].count()
    sumMonthYear.to_frame().reset_index()
    #Get starting data and ending date
    startYear = min(df['date_finished']) - pd.offsets.DateOffset(months=1)
    endYear = max(df['date_finished']) + pd.offsets.DateOffset(months=1)
    #Off set date by one month
    yearList = pd.date_range(startYear, endYear, freq='MS').strftime(dateformat).tolist()
    #Data frame of each month of interest
    numBooks = pd.DataFrame()
    numBooks['monthYear'] = yearList
    #Merge numBooks with sumMonthYear
    booksTotal = pd.merge(numBooks, sumMonthYear, how='outer', on='monthYear')
    #make monthYear datetime
    booksTotal.fillna(0, inplace=True)
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
                                    figsize=(12,6), dpi=300)

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
    #Set plot Title
    fig.suptitle("Books Read through the Years", fontsize=15)

    def animate(i, x, y, l):
        l.set_data(x[:i], y[:i])
        j= i - 1
        if i == 0:
            running.set_text(f'Books finished on {x[i]:%b-%y} :{0}')
        else:
            running.set_text(f'Books finished on {x[j]:%b-%y} : {"+" if booksTotal["diff"][j] != 0 else ""}{booksTotal["diff"][j]:.0f}')
            tally.set_text(f'{y[j]:.0f}')
            tally.xy = (x[j],y[j]+1)
        return l, tally, running

    #Animate Plot
    animation = FuncAnimation(fig, func=animate, frames=booksTotal.shape[0],interval=500, fargs=[x,y,l], blit=True,save_count=0)

    # #Save Plot
    writer = FFMpegWriter(fps=15)
    html = animation.to_html5_video()
    html = html.replace('width="3600" height="1800"','width="900" height="450"')

    return html

def save_file(var):
    var = "{% extends 'bookshelf_analytics.html' %}\n{% block animation %}\n" + var +"\n{% endblock %}"
    file = open("/Users/ricardosaca/Documents/projects/website/website/main/templates/analytics.html","w")
    file.write(var)
    file.close()