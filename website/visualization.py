import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from website.animation import get_books_df
from flask import current_app


def draw_book_viz(df):
    #Data for bar
    df['date_finished'] = pd.to_datetime(df['date_finished'])
    df['year'] = df['date_finished'].dt.year
    counts = df["year"].value_counts()

    #Data for Scatter
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
    booksTotal = pd.merge(sumMonthYear, numBooks, how='outer', on='monthYear')
    #make monthYear datetime
    booksTotal.fillna(0, inplace=True)
    booksTotal['date'] = pd.to_datetime(booksTotal.monthYear.values, format='%b/%y')
    booksTotal = booksTotal.sort_values(by='date')
    #Add a running total and difference column
    booksTotal['total'] = booksTotal.title.cumsum()
    booksTotal['diff'] = booksTotal.total.diff()
    booksTotal['read'] = booksTotal.apply(lambda x: read(df[['title', 'author']].loc[df['monthYear']  == f"{x['monthYear']}"]), axis=1)
    booksTotal.fillna(0, inplace=True)

    #Set values for charting
    dates = pd.to_datetime(booksTotal.monthYear.values, format='%b/%y')
    x = dates
    y = booksTotal.total.values

    # Create figure
    fig = make_subplots(rows=1, cols=2, column_widths=[0.8, 0.3])

    # Add line chart
    fig.add_trace(draw_book_line(booksTotal), row=1, col=1)
    fig['layout']['yaxis'].update(ticks='outside', showline=True, linewidth=1, linecolor='black')
    fig['layout']['xaxis'].update(tickangle=-45,dtick=3, range=[startYear, endYear], ticks='outside', showline=True, linewidth=1, linecolor='black', categoryorder='array', categoryarray=yearList)

    # Add Bar chart
    fig.add_trace(draw_book_bar(counts), row=1, col=2)
    fig['layout']['yaxis2'].update(range=[0, counts.max()+2], side='right', ticks='outside', showline=True, linewidth=1, linecolor='black')
    fig['layout']['xaxis2'].update(ticks='outside', showline=True, linewidth=1, linecolor='black')

    # Add goal line for Bar chart
    goals = {2019:0, 2020:0, 2021: 12, 2022: 18}
    for year, goal in goals.items():
        if goal != 0:
            fig.add_hline(y=goal, line_dash="dot",
                annotation_text= f"Goal for {year} ({goal})",
                annotation_position="bottom left", row=1, col=2)

    #General Fig edits
    fig.update_layout(title_text="Books Read through the Years", title_x=0.5,  title_font_size=18, title_xanchor="center",
                    showlegend=False, height=500)

    return fig


def draw_book_line(booksTotal):
    customdata =  np.stack((booksTotal['diff'], booksTotal['read']), axis=-1)
    fig = go.Scatter(x=booksTotal.monthYear, y=booksTotal.total, customdata=customdata, mode='lines+markers',
                    hovertemplate="<b>Books finished on %{x}: %{customdata[0]}</b><br> %{customdata[1]}<extra></extra>")

    return fig

def draw_book_bar(counts):
    fig = go.Bar(x=counts.index, y=counts.values,
                marker_color='#636EFA',
                text=counts.values, textposition='outside',
                hovertemplate="<b>Read %{y} Books in %{x}</b><extra></extra>")

    return fig

def read(df):
    if df.empty:
        display = f'No books finished'
    else:
        display = "Read: <br>"
        for book in df.iterrows():
            display += f" - {book[1]['title']} by {book[1]['author']}<br>"
    return display