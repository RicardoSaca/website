import pandas as pd
import numpy as np
import textwrap
from plotly.subplots import make_subplots
import plotly.graph_objects as go
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

    endYear = max(df['date_finished']) + (pd.offsets.DateOffset(months=0) if (max(df['date_finished']).month == pd.Timestamp.now().month) else pd.offsets.DateOffset(months=1))
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
    booksTotal.reset_index(inplace=True, drop=True)

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

    # Add year slider for the line chart
    years = sorted(df['year'].dropna().astype(int).unique())   # oldest → newest, left to right
    is_year = booksTotal['date'].dt.year

    def as_list(s):  # Plotly needs None, not NaN, for gaps
        return s.astype(object).where(s.notna(), None).tolist()

    steps = [dict(label='All', method='update',
                args=[{'y': [booksTotal['total'].tolist()]},
                    {'xaxis.range': [-0.5, len(booksTotal) - 0.5],
                        'xaxis.dtick': 3,
                        'yaxis.autorange': True},
                        [0]])]                                   # [0] = only the line trace

    for yr in years:
        mask = is_year == yr
        year_total = booksTotal['title'].where(mask).cumsum()    # 1, 3, 5... within the year; NaN elsewhere
        start, end = booksTotal.index[mask].min(), booksTotal.index[mask].max()
        ymax = year_total.max()
        steps.append(dict(label=str(yr), method='update',
                        args=[{'y': [as_list(year_total)]},
                            {'xaxis.range': [start - 0.5, end + 0.5],
                                'xaxis.dtick': 1,
                                'yaxis.range': [0, ymax + max(1, ymax * 0.1)]},
                                [0]]))

    xdom = fig.layout.xaxis.domain
    fig.update_layout(
        sliders=[dict(
            steps=steps, active=0,
            x=xdom[0], len=xdom[1] - xdom[0],
            y=-0.15, yanchor='top',                    # below the rotated month labels
            currentvalue=dict(visible=False),
            pad=dict(t=0, b=0),
            ticklen=0, minorticklen=0,
            font=dict(size=11, color='black'),
            bgcolor='white', bordercolor='#bbbbbb',
            borderwidth=1, activebgcolor='#636EFA',
        )],
        margin=dict(t=80, b=120),                      # space at the bottom now, not the top
    )
    #General Fig edits
    fig.update_layout(title_text="Books Read through the Years", title_x=0.5, title_font_size=18,
                    title_xanchor="center", showlegend=False, height=560)

    return fig


def draw_book_line(booksTotal):
    customdata =  np.stack((booksTotal['diff'], booksTotal['read']), axis=-1)
    fig = go.Scatter(x=booksTotal['monthYear'], y=booksTotal['total'], customdata=customdata, mode='lines+markers',
                    hovertemplate="<b>Books finished on %{x}: %{customdata[0]}</b><br> %{customdata[1]}<extra></extra>")

    return fig

def draw_book_bar(counts):
    fig = go.Bar(x=counts.index, y=counts.values,
                marker_color='#636EFA',
                text=counts.values, textposition='outside',
                hovertemplate="<b>Read %{y} Books in %{x}</b><extra></extra>")
    return fig

def split_string(text, width):
    # Split the text using textwrap
    wrapped_text = textwrap.wrap(text, width)
    return '<br>\u00A0\u00A0\u00A0\u00A0'.join(wrapped_text)

def read(df):
    if df.empty:
        display = f'No books finished'
    else:
        display = "Read: <br>"
        for book in df.iterrows():
            display_text = split_string(f"{book[1]['title']} by {book[1]['author']}", 50)
            display += f" - {display_text}<br>"
            # display += f" - {book[1]['title']} by {book[1]['author']}<br>"
    return display