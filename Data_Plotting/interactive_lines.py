import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Read data
df = pd.read_csv('sample3.csv')

# Create subplot figure with 2 rows (accel and gyro)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    subplot_titles=("Accelerometer Data", "Gyroscope Data"))

# Custom line dash styles for plotly
line_dash_styles = {
    'Accel_X': 'solid',
    'Accel_Y': 'dash',
    'Accel_Z': 'dot',
    'Gyro_X': 'solid',
    'Gyro_Y': 'dash',
    'Gyro_Z': 'dot',
}

# Colors for lines (r, g, b)
line_colors = {
    'Accel_X': 'red',
    'Accel_Y': 'green',
    'Accel_Z': 'blue',
    'Gyro_X': 'red',
    'Gyro_Y': 'green',
    'Gyro_Z': 'blue',
}

# Helper function to add markers every N points
def add_trace_with_markers(ax, col, row, color, dash_style):
    y_values = df[col]
    x_values = df.index

    # Marker every 10 points
    marker_indices = x_values[::10]
    marker_values = y_values.iloc[::10]

    # Add line trace without markers
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=col,
            line=dict(width=6, dash=dash_style, color=color),
            marker=dict(size=10, symbol='circle', color=color),
            # To show markers only on every 10th point, we will trick by adding invisible markers except those points:
            # But plotly doesn't support per-point marker visibility in a single trace.
            # Workaround: plot full line without markers, then add a separate scatter with only markers at every 10th point.
        ),
        row=row, col=1
    )

    # Add separate marker trace for every 10 points only
    fig.add_trace(
        go.Scatter(
            x=marker_indices,
            y=marker_values,
            mode='markers',
            showlegend=False,
            # marker=dict(size=10, color=color, symbol='circle'),
        ),
        row=row, col=1
    )

# Plot Accelerometer data (row=1)
for col in ['Accel_X', 'Accel_Y', 'Accel_Z']:
    add_trace_with_markers(fig, col, 1, line_colors[col], line_dash_styles[col])

# Plot Gyroscope data (row=2)
for col in ['Gyro_X', 'Gyro_Y', 'Gyro_Z']:
    add_trace_with_markers(fig, col, 2, line_colors[col], line_dash_styles[col])

# Update layout: disable gridlines
fig.update_xaxes(showgrid=False, row=1, col=1)
fig.update_yaxes(showgrid=False, row=1, col=1)
fig.update_xaxes(showgrid=False, row=2, col=1)
fig.update_yaxes(showgrid=False, row=2, col=1)

fig.update_layout(
    height=700,
    width=900,
    title_text="Accelerometer and Gyroscope Data (Interactive Plot)",
    hovermode="x unified"
)

# Update y-axis labels
fig.update_yaxes(title_text="Acceleration", row=1, col=1)
fig.update_yaxes(title_text="Angular Velocity", row=2, col=1)

# Update x-axis label on bottom plot only
fig.update_xaxes(title_text="Sample Index", row=2, col=1)

fig.show()
