import dash
from textwrap import dedent
import dash_core_components as dcc
import dash_html_components as html


def DemoDescriptionCard(markdown_text):
    """
    'width': '80%',
    'max-width': '1024px',
    'font-family': 'Roboto, sans-serif'
    :param markdown_text:
    :return: html.Div
    """
    return html.Div(
            className='row',
            style={
                'padding': '15px 30px 27px',
                'margin': '10px auto 45px',
                'width': '80%',
                'max-width': '1024px',
                'borderRadius': 5,
                'border': 'thin lightgrey solid',
                'font-family': 'Roboto, sans-serif'
            },
            children=dcc.Markdown(dedent(markdown_text))
    )


def demo_explanation(demo_mode):
    if demo_mode:
        return DemoDescriptionCard(
            '''
            ## Getting Started with the Demo
            To get started, select a footage you want to view, and choose the display mode (with or without 
            bounding boxes). Then, you can start playing the video, and the visualization will be displayed depending
            on the current time.
            
            ## What am I looking at?
            This app enhances visualization of objects detected using state-of-the-art Mobile Vision Neural Networks.
            Most user generated videos are dynamic and fast-paced, which might be hard to interpret. A confidence
            heatmap stays consistent through the video and intuitively displays the model predictions. The pie chart
            lets you interpret how the object classes are divided, which is useful when analyzing videos with numerous
            and differing objects.
            
            The purpose of this demo is to explore alternative visualization methods for Object Detection. Therefore, 
            the visualizations, predictions and videos are not generated in real time, but done beforehand. To read 
            more about it, please visit the 
            [project repo](https://github.com/plotly/dash-object-detection).
            '''
        )
