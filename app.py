import os
import pandas as pd
import numpy
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import video_engine as rpd

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True

# Custom Script for Heroku
if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

app.layout = html.Div([
    dcc.Interval(
        id="interval-component",
        interval=500,
        n_intervals=0
    ),

    # Banner display
    html.Div([
        html.H2(
            'App Name',
            id='title'
        ),
        html.Img(
            src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"
        )
    ],
        className="banner"
    ),

    # Body
    html.Div([
        html.Div([
            html.Div(
                rpd.my_Player(
                    id='video-player',
                    url='https://www.youtube.com/watch?v=g9S5GndUhko',
                    width='100%',
                    height='50vh',
                    controls=True,
                    playing=False,
                    seekTo=0,
                    volume=1
                ),
                className="six columns"
            ),

            html.Div([
                dcc.Graph(
                    style={'height': 300},
                    id="bar-score-graph"
                )
            ],
                id="div-all-graphs",
                className="six columns"
            )
        ],
            className="row"
        )
    ],
        className="container"
    )
])


@app.callback(Output("bar-score-graph", "figure"),
              [Input("interval-component", "n_intervals")],
              [State("video-player", "currTime")])
def update_score_bar(n, current_time):
    layout = go.Layout(
        title='Objects Detected',
        showlegend=True,
        margin=go.Margin(l=30, r=30, t=40, b=40)
    )

    if current_time is not None:
        current_frame = round(current_time * 23.98)
        print(current_frame)

        if n > 0 and current_frame > 0:
            # Select the subset of the dataset that correspond to the current frame
            frame_df = video_info_df[video_info_df["frame"] == current_frame]

            print(frame_df.shape)

            # Select up to 5 frames with the highest scores
            frame_df = frame_df[:min(5, frame_df.shape[0])]

            print(frame_df.shape)

            return go.Figure(
                data=[
                    go.Bar(
                        x=frame_df["class_str"].tolist(),
                        y=frame_df["score"].tolist(),
                        name="Object Scores",
                        marker=go.Marker(
                            color="(26, 118, 255)"
                        )
                    )
                ],
                layout=layout
            )

    return go.Figure(
        data=[
            go.Bar(
                x=[1, 2, 3],
                y=[2, 3, 4],
                name="Placeholder",
                marker=go.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        layout=layout
    )


# @app.callback(Output("test", "children"),
#               [Input("interval-component", "n_intervals")])
# def test(n):
#     print("bob")
#     return "bob"


# Load additional CSS to our app
external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",  # Bootstrap
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://rawgit.com/xhlulu/Video-Engine-Dash/master/stylesheet.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})


# Load all the information about our video before the first request is processed
@app.server.before_first_request
def load_data():
    global video_info_df
    video_info_df = pd.read_csv("data/video_info.csv")


# Running the server
if __name__ == '__main__':
    app.run_server(debug=True)
