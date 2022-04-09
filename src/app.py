# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from flask import Flask
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import datetime

from main import get_day_ahead

app = Dash(__name__,)
server = app.server

colors = {
    'background': '#311111',
    'text': '#7FDBFF'
}

zones = ["NO_2", "NO_3"]

df = get_day_ahead(zones)

#fig = go.Figure()
#fig.add_trace(go.Line(df, x="time", y="NO_2" + 25, name="hv", line_shape='hv'))
#fig.add_trace(go.Line(df, x="time", y="NO_3" + 25, name="hv", line_shape='hv'))



#fig = px.line(df, x="year", y="lifeExp", color="country", title="layout.hovermode='x'")
#fig.update_traces(mode="markers+lines", hovertemplate=None)
#fig.update_layout(hovermode="x")


#fig.update_layout(
#    plot_bgcolor=colors['background'],
#    paper_bgcolor=colors['background'],
#    font_color=colors['text']
#)

#app.layout = html.Div(children=[
#    html.H1(children='Hello Dash'),
#
#    html.Div(children='''
#        Dash: A web application framework for your data.
#    '''),
#
#    dcc.Graph(
#        id='example-graph',
#        figure=fig
#    )
#])

app.layout = html.Div(style={}, children=[


    html.Div(children='Day-ahead power price.', style={
        'textAlign': 'center'
    }),

    dcc.Graph(
        id='power-plot',
    ),
    dcc.Interval(
        id='now-line',
        interval=1000, # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    Output("power-plot", "figure"), [Input("now-line", "n_intervals")]
)
def update_now_line(interval):
    global df
    ts = pd.Timestamp.now(tz="Europe/Oslo")
    ts_prev = ts.replace(microsecond=0, second=0, minute=0)
    ts_next = ts_prev + datetime.timedelta(hours=1)

    if ts.minute == 0 and ts.second == 0:
        df = get_day_ahead(zones)

    fig = px.line(df, x="time", y="price", color="zone", line_shape='hv')
    fig.add_vrect(x0=ts_prev, x1=ts_next,
              fillcolor="blue", opacity=0.25, line_width=0)
    fig.update_layout(hovermode="x")

    return fig
