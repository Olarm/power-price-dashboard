# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from flask import Flask
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import datetime
import dateutil
import toml
from collections import namedtuple
from main import get_day_ahead, logger

app = Dash(__name__,)
server = app.server

colors = {
    'background': '#311111',
    'text': '#7FDBFF'
}

def get_zones():
    with open('state.toml', 'r') as f:
        states = toml.load(f)

    Zones = namedtuple("Zones", states["zones"])
    zones = Zones(**states["zones"])
    return zones

zones = get_zones()

app.layout = html.Div(style={}, children=[
    html.Div(
        children=[
            'Day-ahead power price.',
            dcc.Graph(
                id='power-plot',
            ),
            dcc.Interval(
                id='now-line',
                interval=1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Checklist(
                zones.all_zones,
                zones.default_zones,
                id="zones"
            ),
        ],
        style={'textAlign': 'center', 'display': 'inline-block', "width": "70vw"}
    ),
    html.Div(
        children=[
            html.Label('Dropdown'),
            dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),

            html.Br(),
            html.Label('Multi-Select Dropdown'),
            dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
                         ['Montréal', 'San Francisco'],
                         multi=True),

            html.Br(),
            html.Label('Radio Items'),
            dcc.RadioItems(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
        ],
        style={'display': 'inline-block'}
    ),
])


@app.callback(
    Output("power-plot", "figure"), [Input("now-line", "n_intervals")]
)
def update_now_line(interval):
    zones = get_zones()
    try:
        df = pd.read_csv("zone_prices.csv")
    except FileNotFoundError:
        df = get_day_ahead(zones.all_zones)
        df.to_csv("zone_prices.csv")

    ts = pd.Timestamp.now(tz="Europe/Oslo")
    ts_prev = ts.replace(microsecond=0, second=0, minute=0)
    ts_next = ts_prev + datetime.timedelta(hours=1)

    with open('state.toml', 'r') as f:
        states = toml.load(f)
        try:
            prev_ts = pd.to_datetime(states["update"]["timestamp"])
        except dateutil.parser._parser.ParserError:
            logger.warning("Error parsing previous timestamp!")
            prev_ts = ts - datetime.timedelta(hours=1, seconds=1)
            pass

    if prev_ts < ts - datetime.timedelta(hours=1):
        logger.info("Updating data.")
        df = get_day_ahead(zones.all_zones)
        df.to_csv("zone_prices.csv")
        states["update"]["timestamp"] = ts.isoformat()
        with open('state.toml', 'w') as f:
            toml.dump(states, f)

    temp_df = df[df["zone"].isin(zones.chosen_zones)]

    fig = px.line(temp_df, x="time", y="price", color="zone", line_shape='hv')
    fig.add_vrect(x0=ts_prev, x1=ts_next,
              fillcolor="blue", opacity=0.25, line_width=0)
    fig.update_layout(hovermode="x")

    return fig


@app.callback(
    Output("zones", "value"),
    Input("zones", "value")
)
def update_zones(zones_selected):
    with open('state.toml', 'r') as f:
        states = toml.load(f)
        states["zones"]["chosen_zones"] = zones_selected
    with open('state.toml', 'w') as f:
        toml.dump(states, f)
    return zones_selected
