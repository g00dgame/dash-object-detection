import plotly.figure_factory as ff

import os
import pandas as pd
import numpy as np
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
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    # Banner display
    html.Div([
        html.H2(
            'Object Detection Dashboard',
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
                html.Div([
                    dcc.Dropdown(
                        options=[
                            {'label': 'Visual Mode', 'value': 'visual'},
                            {'label': 'Detection Mode', 'value': 'detection'}
                        ],
                        value='visual',
                        id="dropdown-mode-selection",
                        searchable=False,
                        clearable=False
                    )
                ],
                    style={'margin-bottom': '20px'}
                ),
                html.Div([
                    rpd.my_Player(
                        id='video-display',
                        url='https://www.youtube.com/watch?v=g9S5GndUhko',
                        width='100%',
                        height='50vh',
                        controls=True,
                        playing=False,
                        seekTo=0,
                        volume=1
                    )
                ],
                    style={'color': 'rgb(255, 255, 255)'}
                ),
            ],
                className="six columns"
            ),

            html.Div(id="div-visual-mode", className="six columns"),

            html.Div(id="div-detection-mode", className="six columns")
        ],
            className="row"
        )
    ],
        className="container"
    )
])


@app.callback(Output("div-visual-mode", "children"),
              [Input("dropdown-mode-selection", "value")])
def update_visual_mode(value):
    if value == "visual":
        return [
            dcc.Interval(
                id="interval-visual-mode",
                interval=800,
                n_intervals=0
            ),

            dcc.Graph(
                style={'height': 400},
                id="heatmap-confidence"
            ),

            dcc.Graph(
                style={'height': 300},
                id="pie-object-count"
            )
        ]

    else:
        return []


@app.callback(Output("div-detection-mode", "children"),
              [Input("dropdown-mode-selection", "value")])
def update_detection_mode(value):
    if value == "detection":
        return [
            dcc.Interval(
                id="interval-detection-mode",
                interval=800,
                n_intervals=0
            ),

            dcc.Graph(
                style={'height': 300},
                id="bar-score-graph"
            )
        ]
    else:
        return []


@app.callback(Output("bar-score-graph", "figure"),
              [Input("interval-detection-mode", "n_intervals")],
              [State("video-display", "currTime")])
def update_score_bar(n, current_time):
    layout = go.Layout(
        title='Detection Scores (High to Low)',
        showlegend=False,
        margin=go.Margin(l=70, r=40, t=50, b=30),
        yaxis={'title': 'Score'}
    )

    if current_time is not None:
        current_frame = round(current_time * 23.98)

        if n > 0 and current_frame > 0:
            # Select the subset of the dataset that correspond to the current frame
            frame_df = video_info_df[video_info_df["frame"] == current_frame]

            # Select up to 5 frames with the highest scores
            frame_df = frame_df[:min(8, frame_df.shape[0])]

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

    return go.Figure(data=[go.Bar()], layout=layout)  # Returns empty bar


@app.callback(Output("pie-object-count", "figure"),
              [Input("interval-visual-mode", "n_intervals")],
              [State("video-display", "currTime")])
def update_object_count_pie(n, current_time):
    layout = go.Layout(
        title='Object Count',
        showlegend=True,
        margin=go.Margin(l=50, r=30, t=30, b=40)
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

    return go.Figure(data=[go.Pie()], layout=layout)  # Returns empty pie chart


@app.callback(Output("heatmap-confidence", "figure"),
              [Input("interval-visual-mode", "n_intervals")],
              [State("video-display", "currTime")])
def update_heatmap_confidence(n, current_time):
    layout = go.Layout(
        title="Confidence Heatmap",
        margin=go.Margin(l=20, r=20, t=57, b=30)
    )

    if current_time is not None:
        current_frame = round(current_time * 23.98)

        if n > 0 and current_frame > 0:
            # Select the subset of the dataset that correspond to the current frame
            frame_df = video_info_df[video_info_df["frame"] == current_frame]

            # Remove duplicate, keep the top result
            frame_no_dup = frame_df[["class_str", "score"]].drop_duplicates("class_str")
            frame_no_dup.set_index("class_str", inplace=True)

            # The list of scores
            score_list = []
            for el in classes_padded:
                if el in frame_no_dup.index.values:
                    score_list.append(frame_no_dup.loc[el][0])
                else:
                    score_list.append(0)

            # Generate the score matrix, and flip it for visual
            score_matrix = np.reshape(score_list, (-1, int(root_round)))
            score_matrix = np.flip(score_matrix, axis=0)

            # We set the color scale to white if there's nothing in the frame_no_dup
            if frame_no_dup.shape != (0, 1):
                colorscale = [[0, '#ffffff'], [1, '#f71111']]
                font_colors = ['#3c3636', '#efecee']
            else:
                colorscale = [[0, '#ffffff'], [1, '#ffffff']]
                font_colors = ['#3c3636']

            hover_text = [f"{score * 100:.2f}% confidence" for score in score_list]
            hover_text = np.reshape(hover_text, (-1, int(root_round)))
            hover_text = np.flip(hover_text, axis=0)



            pt = ff.create_annotated_heatmap(
                score_matrix,
                annotation_text=classes_matrix,
                colorscale=colorscale,
                font_colors=font_colors,
                hoverinfo='text',
                text=hover_text
            )

            pt.layout.title = layout.title
            pt.layout.margin = layout.margin

            return pt

    # Returns empty figure
    return go.Figure(data=[go.Pie()], layout=layout)


# Load additional CSS to our app
external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://rawgit.com/xhlulu/dash-object-detection/master/stylesheet.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})


@app.server.before_first_request
def load_data():
    global video_info_df, n_classes, classes_matrix, classes_padded, root_round

    # Load the dataframe containing all the processed object detections inside the video
    video_info_df = pd.read_csv("data/video_info.csv")

    # The list of classes, and the number of classes
    classes_list = video_info_df["class_str"].value_counts().index.tolist()
    n_classes = len(classes_list)

    # Gets the smallest value needed to add to the end of the classes list to get a square matrix
    root_round = round(np.sqrt(len(classes_list)))
    total_size = root_round ** 2
    padding_value = int(total_size - n_classes)
    classes_padded = np.pad(classes_list, (0, padding_value), mode='constant')

    # The padded matrix containing all the classes inside a matrix
    classes_matrix = np.reshape(classes_padded, (int(root_round), int(root_round)))

    # Flip it for better looks
    classes_matrix = np.flip(classes_matrix, axis=0)


# Running the server
if __name__ == '__main__':
    app.run_server(debug=True)
