import plotly.graph_objects as go

def plot_timeseries(time_series1, time_series2, labels):
    """
    Function to plot two time series on the same axis using Plotly.

    Args:
        time_series1: A pandas Series with the dates as the index.
        time_series2: A pandas Series with the dates as the index.
        labels: A list of labels for the two time series and title.
    """
    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(
        x=time_series1.index,
        y=time_series1.values,
        mode='lines',
        name=labels[0],
    ))

    fig.add_trace(go.Scatter(
        x=time_series2.index,
        y=time_series2.values,
        mode='lines',
        name=labels[1],
    ))

    # Set layout attributes
    fig.update_layout(
        title=labels[2],
        xaxis_title="Time",
        yaxis_title="Value",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )

    fig.show()
