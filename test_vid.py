import random

import dash
import datetime
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
import pandas as pd
from collections import deque

import video_engine as rpd

app = dash.Dash()

app.scripts.config.serve_locally = True 
X = deque(maxlen=1)
Y = deque(maxlen=1)
X.append(1)
Y.append(1)

newtime = deque(maxlen=0)

df = pd.read_csv('CleanData.csv') #Reads CSV Data


app.layout = html.Div(children=[
    dcc.Interval(
        id="interval-component",
        interval=200,
        n_intervals=0
    ),

    html.H1(children='the best fucking data analyzer ever',
            style={
                'textAlign': 'center'
                    }),
    dcc.Graph(id='sens1'),
 #   html.H2(id = 'time_counter',
     #    children='''NO TIME YET''',
   #      style={
  #              'textAlign': 'center'
   #                 }),
    html.Div(children=rpd.my_Player(
        id = 'video_player',
        url = 'https://www.youtube.com/watch?v=g9S5GndUhko',
        width = 900,
        height = 720,
        controls = True,
        playing = False,
        seekTo = 0,
        volume = 1 ),
        style={'textAlign': 'center'}
    ),
dcc.Slider(id = 'time-slider', value=0, min=0, max=120, step=0.00001,
           marks={0: 'Start', 120: 'End'}),

    
    ])


@app.callback( ##Graph 1
    dash.dependencies.Output('sens1', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')],
    [dash.dependencies.State('video_player', 'currTime')])
def update_time(n, newtime):
    X.append(newtime)
    data = go.Scatter(
                x = df['timestamp'],
                y = df['sens1'],
                name = 'Scatter',
                mode = 'lines'
        )
    
    return {'data': [data], 'layout': go.Layout(xaxis = dict(range=[min(X), max(X)], fixedrange='true'),)}


# TESTING
#  Tested
#   Playing (True or False)
#   Volume (between 0 and 1)
#   seekTo
#   muted
#   playbackRate
#  To BE Tested
#   getCurrentTime
#   getDuration
#   controls (volume only)
#   styles
#   playsInline
#   config


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

app.css.append_css({
    'external_url': 'https://unpkg.com/video-react@0.9.4/dist/video-react.css'})

if __name__ == '__main__':
    app.run_server(debug=True)
