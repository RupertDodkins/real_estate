import numpy as np
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display, Image

def plot_timeseries(column_pairs, df1, df2, title='', df_titles=[], colors=['blue', 'red'], dynamic=False):
    """
    Function to plot pairs of time series on the same axes using Plotly.

    Args:
        column_pairs: A list of tuples or strings. Each tuple represents a pair of column headers.
        df1: A pandas DataFrame containing the first set of time series.
        df2: A pandas DataFrame containing the second set of time series.
    """
    n = len(column_pairs)
    cols = 3 if n >= 3 else n
    rows = math.ceil(n / 3)

    fig = make_subplots(rows=rows, cols=cols, horizontal_spacing=0.1)

    for i, pair in enumerate(column_pairs, start=1):
        row = math.ceil(i / 3)
        col = i % 3 if i % 3 != 0 else 3

        # Check if pair is a single string or a tuple of two strings
        if isinstance(pair, tuple):
            label, pair = pair
            col1, col2 = pair
        elif isinstance(pair, str):
            label = col1 = col2 = pair
        else:
            raise ValueError('Each item in column_pairs must be either a string or a tuple of two strings.')

        # Add traces
        fig.add_trace(go.Scatter(
            x=df1.index,
            y=df1[col1].values,
            mode='lines',
            name=df_titles[0],
            # name=f'{col1} (df1)',
            line=dict(width=2, color=colors[0]),
            marker=dict(color=colors[0])
        ), row=row, col=col)

        fig.add_trace(go.Scatter(
            x=df2.index,
            y=df2[col2].values,
            mode='lines',
            name=df_titles[1],
            # name=f'{col2} (df2)',
            line=dict(width=2, color=colors[1]),
            marker=dict(color=colors[1])
        ), row=row, col=col)

        if i == 1:
            fig['layout']['yaxis'].update(title_text=label)
            fig['layout']['xaxis'].update(title_text='Years')
        else:
            fig['layout'][f'yaxis{i}'].update(title_text=label)
            fig['layout'][f'xaxis{i}'].update(title_text='Years')
    
    for i in range(1, len(fig['data'])//2):
        fig['data'][2*i]['showlegend']=False
        fig['data'][2*i +1]['showlegend']=False   

    # Set layout attributes
    fig.update_layout(
        title_text=title,
        xaxis_title='Months',
        # yaxis_title="Value",
        width=1300,
        height=600*rows,
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )



    if dynamic:
        fig.show()
    else:
        image_bytes = fig.to_image(format='png')
        display(Image(image_bytes))