import os
import pandas as pd
import numpy
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from PIL import ImageColor
import video_engine as rpd
from utils import STANDARD_COLORS

app = dash.Dash(__name__)
server = app.server

# Custom Script for Heroku
if 'DYNO' in os.environ:
    app.scripts.config.serve_locally = False
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

app.scripts.config.serve_locally = True

app.layout = html.Div([
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
            html.Div([
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

                dcc.RadioItems(
                    options=[
                        {'label': 'Visual Mode', 'value': 'visual'},
                        {'label': 'Detection Mode', 'value': 'detection'}
                    ],
                    value='detection',
                    labelStyle={'display': 'inline-block'}
                )
            ],
                className="six columns"
            ),

            html.Div([
                dcc.Interval(
                    id="interval-component",
                    interval=800,
                    n_intervals=0
                ),

                dcc.Graph(
                    style={'height': 300},
                    id="bar-score-graph"
                ),

                dcc.Graph(
                    style={'height': 300},
                    id="pie-object-count"
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
        title='Detection Scores (High to Low)',
        showlegend=False,
        margin=go.Margin(l=50, r=30, t=40, b=40),
        yaxis={'title': 'Score'}
    )

    if current_time is not None:
        current_frame = round(current_time * 23.98)

        if n > 0 and current_frame > 0:
            # Select the subset of the dataset that correspond to the current frame
            frame_df = video_info_df[video_info_df["frame"] == current_frame]

            # Select up to 5 frames with the highest scores
            frame_df = frame_df[:min(5, frame_df.shape[0])]

            # Add count to object names (e.g. person --> person 1, person --> person 2)
            objects = frame_df["class_str"].tolist()
            object_count_dict = {x: 0 for x in set(objects)}  # Keeps count of the objects
            objects_wc = []  # Object renamed with counts
            for object in objects:
                object_count_dict[object] += 1  # Increment count
                objects_wc.append(f"{object} {object_count_dict[object]}")

            # Add text information
            y_text = [f"{round(value*100)}% confidence" for value in frame_df["score"].tolist()]

            # Convert color into rgb
            color_map = lambda class_id: str(ImageColor.getrgb(STANDARD_COLORS[class_id % len(STANDARD_COLORS)]))
            colors = ["rgb" + color_map(class_id) for class_id in frame_df["class"].tolist()]

            bar = go.Bar(
                x=objects_wc,
                y=frame_df["score"].tolist(),
                text=y_text,
                name="Detection Scores",
                hoverinfo="x+text",
                marker=go.Marker(
                    color=colors,
                    line=dict(
                        color='rgb(79, 85, 91)',
                        width=1
                    )
                )
            )

            return go.Figure(data=[bar], layout=layout)

    return go.Figure(
        data=[
            go.Bar(
                x=[],
                y=[],
                name="Placeholder",
                marker=go.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        layout=layout
    )


@app.callback(Output("pie-object-count", "figure"),
              [Input("interval-component", "n_intervals")],
              [State("video-player", "currTime")])
def update_object_count_pie(n, current_time):
    layout = go.Layout(
        title='Object Count',
        showlegend=True,
        margin=go.Margin(l=50, r=30, t=40, b=40),
        yaxis={'title': 'Score'}
    )

    if current_time is not None:
        current_frame = round(current_time * 23.98)

        if n > 0 and current_frame > 0:
            # Select the subset of the dataset that correspond to the current frame
            frame_df = video_info_df[video_info_df["frame"] == current_frame]

            # Get the count of each object class
            class_counts = frame_df["class_str"].value_counts()

            classes = class_counts.index.tolist()  # List of each class
            counts = class_counts.tolist()  # List of each count

            text = [f"{count} detected" for count in counts]

            pie = go.Pie(
                labels=classes,
                values=counts,
                text=text,
                hoverinfo="text+percent",
                textinfo="label+percent"
            )

            return go.Figure(data=[pie], layout=layout)

    return go.Figure()


# Load additional CSS to our app
external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://rawgit.com/xhlulu/dash-object-detection/master/stylesheet.css"
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
