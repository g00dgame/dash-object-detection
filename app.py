import os
from textwrap import dedent

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
from dash.dependencies import Input, Output, State

import dash_player as player
from utils.coco_colors import STANDARD_COLORS
import utils.dash_reusable_components as drc

DEBUG = True
FRAMERATE = 24.0

app = dash.Dash(__name__)
server = app.server

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True


def load_data(path):
    """Load data about a specific footage (given by the path). It returns a dictionary of useful variables such as
    the dataframe containing all the detection and bounds localization, the number of classes inside that footage,
    the matrix of all the classes in string, the given class with padding, and the root of the number of classes,
    rounded."""

    # Load the dataframe containing all the processed object detections inside the video
    video_info_df = pd.read_csv(path)

    # The list of classes, and the number of classes
    classes_list = video_info_df["class_str"].value_counts().index.tolist()
    n_classes = len(classes_list)

    # Gets the smallest value needed to add to the end of the classes list to get a square matrix
    root_round = np.ceil(np.sqrt(len(classes_list)))
    total_size = root_round ** 2
    padding_value = int(total_size - n_classes)
    classes_padded = np.pad(classes_list, (0, padding_value), mode='constant')

    # The padded matrix containing all the classes inside a matrix
    classes_matrix = np.reshape(classes_padded, (int(root_round), int(root_round)))

    # Flip it for better looks
    classes_matrix = np.flip(classes_matrix, axis=0)

    data_dict = {
        "video_info_df": video_info_df,
        "n_classes": n_classes,
        "classes_matrix": classes_matrix,
        "classes_padded": classes_padded,
        "root_round": root_round
    }

    if DEBUG:
        print(f'{path} loaded.')

    return data_dict


# def markdown_popup():
#     return html.Div(
#         id='markdown',
#         className="model",
#         style={'display': 'none'},
#         children=(
#             html.Div(
#                 style={'width': '60vw', 'margin': '10% auto'},
#                 children=[
#                     html.Div(
#                         width=100,
#                         padding=0,
#                         margin=0,
#                         type='flat',
#                         children=html.Button(
#                             "Close",
#                             id="markdown_close",
#                             n_clicks=0,
#                             className="closeButton",
#                             style={'color': 'var(--text)', 'border': 'none', 'height': '100%'}
#                         )
#                     ),
#                     html.Div(
#                         width=100,
#                         margin=0,
#                         padding=10,
#                         children=[dcc.Markdown(
#                             children=dedent(
#                                 '''
#                                 ##### What am I looking at?
#                                 This app enhances visualization of objects detected using state-of-the-art Mobile Vision Neural Networks.
#                                 Most user generated videos are dynamic and fast-paced, which might be hard to interpret. A confidence
#                                 heatmap stays consistent through the video and intuitively displays the model predictions. The pie chart
#                                 lets you interpret how the object classes are divided, which is useful when analyzing videos with numerous
#                                 and differing objects.
#
#                                 ##### More about this dash app
#                                 The purpose of this demo is to explore alternative visualization methods for Object Detection. Therefore,
#                                 the visualizations, predictions and videos are not generated in real time, but done beforehand. To read
#                                 more about it, please visit the [project repo](https://github.com/plotly/dash-object-detection).
#
#                                 '''
#                             ))
#                         ]
#                     )
#                 ]
#             )
#         )
#     )
#

# Main App


# Main App

app.layout = html.Div(
    children=[
        html.Div(
            id='top-bar',
            className='row',
            style={'background-color': '#fa4f56',
                   'height': '5px',
                   }
        ),
        # main app body
        html.Div(
            children=[
                html.Div(
                    id='left-side-column',
                    className='eight columns',
                    style={'display': 'flex',
                           'flexDirection': 'column',
                           'flex': 1,
                           'height': 'calc(100vh - 5px)',
                           # 'overflow-y': 'scroll',
                           'backgroundColor': '#F9F9F9',
                           'justifyContent': 'space-around',
                           'alignItems': 'center',
                           'border': '1px solid black'},
                    children=[
                        html.Div(
                            id='header-section',  # todo: set font for header and body
                            children=[
                                html.H4(
                                    'Object Detection Explorer',
                                ),
                                html.P(
                                    'To get started, select a footage you want to view, and choose the display mode (with or without'
                                    ' bounding boxes). Then, you can start playing the video, and the visualization will '
                                    'be displayed depending on the current time.'
                                ),
                                html.Button("Learn More", id="learn-more-button", n_clicks=0)
                            ]
                        ),
                        html.Div(id='video-player', style={'height': '200px', 'width': '300px', 'border': '1px solid'}),
                        html.Div(
                            className='control-section',
                            children=[
                                html.Div(
                                    className='control-element',
                                    children=[
                                        html.Div(children=["Minimum Confidence Threshold:"], style={'width': '40%'}),
                                        html.Div(dcc.Slider(
                                            id='slider-minimum-confidence-threshold',
                                            min=20,
                                            max=80,
                                            marks={i: f'{i}%' for i in range(20, 81, 10)},
                                            value=50,
                                            updatemode='drag'
                                        ), style={'width': '60%'})
                                    ]
                                ),

                                html.Div(
                                    className='control-element',
                                    children=[
                                        html.Div(children=["Footage Selection:"], style={'width': '40%'}),
                                        dcc.Dropdown(
                                            id="dropdown-footage-selection",
                                            options=[
                                                {'label': 'Drone recording of canal festival',
                                                 'value': 'DroneCanalFestival'},
                                                {'label': 'Drone recording of car festival', 'value': 'car_show_drone'},
                                                {'label': 'Drone recording of car festival #2',
                                                 'value': 'DroneCarFestival2'},
                                                {'label': 'Drone recording of a farm', 'value': 'FarmDrone'},
                                                {'label': 'Lion fighting Zebras', 'value': 'zebra'},
                                                {'label': 'Man caught by a CCTV', 'value': 'ManCCTV'},
                                                {'label': 'Man driving expensive car', 'value': 'car_footage'},
                                                {'label': 'Restaurant Robbery', 'value': 'RestaurantHoldup'}
                                            ],
                                            value='car_show_drone',
                                            clearable=False,
                                            style={'width': '60%'}
                                        )
                                    ]
                                ),

                                html.Div(
                                    className='control-element',
                                    children=[
                                        html.Div(children=["Video Display Mode:"], style={'width': '40%'}),
                                        dcc.Dropdown(
                                            id="dropdown-video-display-mode",
                                            options=[
                                                {'label': 'Regular Display', 'value': 'regular'},
                                                {'label': 'Display with Bounding Boxes', 'value': 'bounding_box'},
                                            ],
                                            value='bounding_box',
                                            searchable=False,
                                            clearable=False,
                                            style={'width': '60%'}
                                        )
                                    ]
                                ),

                                html.Div(
                                    className='control-element',
                                    children=[
                                        html.Div(children=["Graph View Mode:"], style={'width': '40%'}),
                                        dcc.Dropdown(
                                            id="dropdown-graph-view-mode",
                                            options=[
                                                {'label': 'Visual Mode', 'value': 'visual'},
                                                {'label': 'Detection Mode', 'value': 'detection'}
                                            ],
                                            value='visual',
                                            searchable=False,
                                            clearable=False,
                                            style={'width': '60%'}
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        html.Div(
            id='right-side-column',
            className='four columns',
            style={
                   'height': 'calc(100vh - 5px)',
                   'overflow-y': 'scroll',
                   'backgroundColor': '#F9F9F9',
                   'border': '1px solid black',
                'marginLeft': '0px',
                'float':'right'
                   },
            children=[
                html.Img(
                    style={'width': '100px', 'margin': '2px', 'float': 'right', 'display': 'inline-block'},
                    src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png"),
                html.Div(id="div-visual-mode", style={'width': '100%'})
            ]
        )
    ]
    # markdown_popup()
)


# Data Loading
@app.server.before_first_request
def load_all_footage():
    global data_dict, url_dict

    # Load the dictionary containing all the variables needed for analysis
    data_dict = {
        'james_bond': load_data("data/james_bond_object_data.csv"),
        'zebra': load_data("data/Zebra_object_data.csv"),
        'car_show_drone': load_data("data/CarShowDrone_object_data.csv"),
        'car_footage': load_data("data/CarFootage_object_data.csv"),
        'DroneCanalFestival': load_data("data/DroneCanalFestivalDetectionData.csv"),
        'DroneCarFestival2': load_data("data/DroneCarFestival2DetectionData.csv"),
        'FarmDrone': load_data("data/FarmDroneDetectionData.csv"),
        'ManCCTV': load_data("data/ManCCTVDetectionData.csv"),
        'RestaurantHoldup': load_data("data/RestaurantHoldupDetectionData.csv")
    }

    url_dict = {
        'regular': {
            'james_bond': 'https://www.youtube.com/watch?v=g9S5GndUhko',
            'zebra': 'https://www.youtube.com/watch?v=TVvtD3AVt10',
            'car_show_drone': 'https://www.youtube.com/watch?v=gPtn6hD7o8g',
            'car_footage': 'https://www.youtube.com/watch?v=qX3bDxHuq6I',
            'DroneCanalFestival': 'https://youtu.be/0oucTt2OW7M',
            'DroneCarFestival2': 'https://youtu.be/vhJ7MHsJvwY',
            'FarmDrone': 'https://youtu.be/aXfKuaP8v_A',
            'ManCCTV': 'https://youtu.be/BYZORBIxgbc',
            'RestaurantHoldup': 'https://youtu.be/WDin4qqgpac',
        },

        'bounding_box': {
            'james_bond': 'https://www.youtube.com/watch?v=g9S5GndUhko',
            'zebra': 'https://www.youtube.com/watch?v=G2pbZgyWQ5E',
            'car_show_drone': 'https://www.youtube.com/watch?v=9F5FdcVmLOY',
            'car_footage': 'https://www.youtube.com/watch?v=EhnNosq1Lrc',
            'DroneCanalFestival': 'https://youtu.be/6ZZmsnwk2HQ',
            'DroneCarFestival2': 'https://youtu.be/2Gr4RQ-JHIs',
            'FarmDrone': 'https://youtu.be/pvvW5yZlpyc',
            'ManCCTV': 'https://youtu.be/1oMrHLrtOZw',
            'RestaurantHoldup': 'https://youtu.be/HOIKOwixYEY',
        }
    }


# Footage Selection
@app.callback(Output("video-display", "url"),
              [Input('dropdown-footage-selection', 'value'),
               Input('dropdown-video-display-mode', 'value')])
def select_footage(footage, display_mode):
    # Find desired footage and update player video
    url = url_dict[display_mode][footage]
    return url


# # Learn more popup
# @app.callback(Output("markdown", "style"),
#               [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")])
# def update_click_output(button_click, close_click):
#     if button_click > close_click:
#         return {"display": "block"}
#     else:
#         return {"display": "none"}


# Graph View Selection
@app.callback(Output("div-visual-mode", "children"),
              [Input("dropdown-graph-view-mode", "value")])
def update_visual_mode(value):
    if value == "visual":
        return [
            dcc.Interval(
                id="interval-visual-mode",
                interval=700,
                n_intervals=0
            ),

            dcc.Graph(
                id="heatmap-confidence"
            ),

            dcc.Graph(
                id="pie-object-count"
            )
        ]

    else:
        return []


#
#
# @app.callback(Output("div-detection-mode", "children"),
#               [Input("dropdown-graph-view-mode", "value")])
# def update_detection_mode(value):
#     if value == "detection":
#         return [
#             dcc.Interval(
#                 id="interval-detection-mode",
#                 interval=700,
#                 n_intervals=0
#             ),
#
#             dcc.Graph(
#                 style={'height': '50vh'},
#                 id="bar-score-graph"
#             )
#         ]
#     else:
#         return []
#
#
# # Updating Figures
# @app.callback(Output("bar-score-graph", "figure"),
#               [Input("interval-detection-mode", "n_intervals")],
#               [State("video-display", "currTime"),
#                State('dropdown-footage-selection', 'value'),
#                State('slider-minimum-confidence-threshold', 'value')])
# def update_score_bar(n, current_time, footage, threshold):
#     layout = go.Layout(
#         title='Detection Score of Most Probable Objects',
#         showlegend=False,
#         margin=go.Margin(l=70, r=40, t=50, b=30),
#         yaxis={
#             'title': 'Score',
#             'range': [0,1]
#         }
#     )
#
#     if current_time is not None:
#         current_frame = round(current_time * FRAMERATE)
#
#         if n > 0 and current_frame > 0:
#             video_info_df = data_dict[footage]["video_info_df"]
#
#             # Select the subset of the dataset that correspond to the current frame
#             frame_df = video_info_df[video_info_df["frame"] == current_frame]
#
#             # Select only the frames above the threshold
#             threshold_dec = threshold/100  # Threshold in decimal
#             frame_df = frame_df[frame_df["score"] > threshold_dec]
#
#             # Select up to 8 frames with the highest scores
#             frame_df = frame_df[:min(8, frame_df.shape[0])]
#
#             # Add count to object names (e.g. person --> person 1, person --> person 2)
#             objects = frame_df["class_str"].tolist()
#             object_count_dict = {x: 0 for x in set(objects)}  # Keeps count of the objects
#             objects_wc = []  # Object renamed with counts
#             for object in objects:
#                 object_count_dict[object] += 1  # Increment count
#                 objects_wc.append(f"{object} {object_count_dict[object]}")
#
#             # Add text information
#             y_text = [f"{round(value*100)}% confidence" for value in frame_df["score"].tolist()]
#
#             # Convert color into rgb
#             color_map = lambda class_id: str(ImageColor.getrgb(STANDARD_COLORS[class_id % len(STANDARD_COLORS)]))
#             colors = ["rgb" + color_map(class_id) for class_id in frame_df["class"].tolist()]
#
#             bar = go.Bar(
#                 x=objects_wc,
#                 y=frame_df["score"].tolist(),
#                 text=y_text,
#                 name="Detection Scores",
#                 hoverinfo="x+text",
#                 marker=go.Marker(
#                     color=colors,
#                     line=dict(
#                         color='rgb(79, 85, 91)',
#                         width=1
#                     )
#                 )
#             )
#
#             return go.Figure(data=[bar], layout=layout)
#
#     return go.Figure(data=[go.Bar()], layout=layout)  # Returns empty bar
#
#
# @app.callback(Output("pie-object-count", "figure"),
#               [Input("interval-visual-mode", "n_intervals")],
#               [State("video-display", "currTime"),
#                State('dropdown-footage-selection', 'value'),
#                State('slider-minimum-confidence-threshold', 'value')])
# def update_object_count_pie(n, current_time, footage, threshold):
#     layout = go.Layout(
#         title='Object Count',
#         showlegend=True,
#         margin=go.Margin(l=50, r=30, t=30, b=40)
#     )
#
#     if current_time is not None:
#         current_frame = round(current_time * FRAMERATE)
#
#         if n > 0 and current_frame > 0:
#             video_info_df = data_dict[footage]["video_info_df"]
#
#             # Select the subset of the dataset that correspond to the current frame
#             frame_df = video_info_df[video_info_df["frame"] == current_frame]
#
#             # Select only the frames above the threshold
#             threshold_dec = threshold/100  # Threshold in decimal
#             frame_df = frame_df[frame_df["score"] > threshold_dec]
#
#             # Get the count of each object class
#             class_counts = frame_df["class_str"].value_counts()
#
#             classes = class_counts.index.tolist()  # List of each class
#             counts = class_counts.tolist()  # List of each count
#
#             text = [f"{count} detected" for count in counts]
#
#             pie = go.Pie(
#                 labels=classes,
#                 values=counts,
#                 text=text,
#                 hoverinfo="text+percent",
#                 textinfo="label+percent"
#             )
#
#             return go.Figure(data=[pie], layout=layout)
#
#     return go.Figure(data=[go.Pie()], layout=layout)  # Returns empty pie chart
#
#
# @app.callback(Output("heatmap-confidence", "figure"),
#               [Input("interval-visual-mode", "n_intervals")],
#               [State("video-display", "currTime"),
#                State('dropdown-footage-selection', 'value'),
#                State('slider-minimum-confidence-threshold', 'value')])
# def update_heatmap_confidence(n, current_time, footage, threshold):
#     layout = go.Layout(
#         title="Confidence Level of Object Presence",
#         margin=go.Margin(l=20, r=20, t=57, b=30)
#     )
#
#     if current_time is not None:
#         current_frame = round(current_time * FRAMERATE)
#
#         if n > 0 and current_frame > 0:
#             # Load variables from the data dictionary
#             video_info_df = data_dict[footage]["video_info_df"]
#             classes_padded = data_dict[footage]["classes_padded"]
#             root_round = data_dict[footage]["root_round"]
#             classes_matrix = data_dict[footage]["classes_matrix"]
#
#             # Select the subset of the dataset that correspond to the current frame
#             frame_df = video_info_df[video_info_df["frame"] == current_frame]
#
#             # Select only the frames above the threshold
#             threshold_dec = threshold / 100
#             frame_df = frame_df[frame_df["score"] > threshold_dec]
#
#             # Remove duplicate, keep the top result
#             frame_no_dup = frame_df[["class_str", "score"]].drop_duplicates("class_str")
#             frame_no_dup.set_index("class_str", inplace=True)
#
#             # The list of scores
#             score_list = []
#             for el in classes_padded:
#                 if el in frame_no_dup.index.values:
#                     score_list.append(frame_no_dup.loc[el][0])
#                 else:
#                     score_list.append(0)
#
#             # Generate the score matrix, and flip it for visual
#             score_matrix = np.reshape(score_list, (-1, int(root_round)))
#             score_matrix = np.flip(score_matrix, axis=0)
#
#             # We set the color scale to white if there's nothing in the frame_no_dup
#             if frame_no_dup.shape != (0, 1):
#                 colorscale = [[0, '#ffffff'], [1, '#f71111']]
#                 font_colors = ['#3c3636', '#efecee']
#             else:
#                 colorscale = [[0, '#ffffff'], [1, '#ffffff']]
#                 font_colors = ['#3c3636']
#
#             hover_text = [f"{score * 100:.2f}% confidence" for score in score_list]
#             hover_text = np.reshape(hover_text, (-1, int(root_round)))
#             hover_text = np.flip(hover_text, axis=0)
#
#             pt = ff.create_annotated_heatmap(
#                 score_matrix,
#                 annotation_text=classes_matrix,
#                 colorscale=colorscale,
#                 font_colors=font_colors,
#                 hoverinfo='text',
#                 text=hover_text,
#                 zmin=0,
#                 zmax=1
#             )
#
#             pt.layout.title = layout.title
#             pt.layout.margin = layout.margin
#
#             return pt
#
#     # Returns empty figure
#     return go.Figure(data=[go.Pie()], layout=layout)
#
#
# external_css = [
#     "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
#     "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
#     "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
#     "https://cdn.rawgit.com/xhlulu/9a6e89f418ee40d02b637a429a876aa9/raw/base-styles.css",
#     "https://cdn.rawgit.com/plotly/dash-object-detection/875fdd6b/custom-styles.css"
# ]
#
# for css in external_css:
#     app.css.append_css({"external_url": css})


# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=DEBUG, host='0.0.0.0')
