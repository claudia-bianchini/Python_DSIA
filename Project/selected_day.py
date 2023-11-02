import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Sample data generation for demonstration
data = pd.date_range('2023-01-01', '2023-12-31')

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Slider for Days in a Year"),
    html.Div(id='display-selected-day'),
    
    dcc.Slider(
        id='day-slider',
        min=0,
        max=len(data) - 1,
        marks={i: str(date.strftime('%Y-%m-%d')) for i, date in enumerate(data)},
        value=0,  # Initial value for the slider
        step=1
    )
])

@app.callback(
    Output('display-selected-day', 'children'),
    Input('day-slider', 'value')
)
def update_date(value):
    selected_date = data[value].strftime('%Y-%m-%d')
    return f"Selected Day: {selected_date}"

if __name__ == '__main__':
    app.run_server(debug=True)
