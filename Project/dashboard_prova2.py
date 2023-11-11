import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import folium

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Dashboard with Map"),
    html.Div([
        html.Label("Latitude:"),
        dcc.Input(id="latitude-input", type="number", value=0),
    ]),
    html.Div([
        html.Label("Longitude:"),
        dcc.Input(id="longitude-input", type="number", value=0),
    ]),
    html.Div(id='map-container'),
])

# Callback to update the map based on the input
@app.callback(
    Output("map-container", "children"),
    Input("latitude-input", "value"),
    Input("longitude-input", "value"),
)
def update_map(latitude, longitude):
    # Create a Folium map centered on the provided coordinates
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # Add markers, popups, or other map elements here
    # For example: folium.Marker([latitude, longitude], popup='My Marker').add_to(m)

    # Convert the Folium map to an HTML string
    map_html = m.get_root().render()

    return [html.Div([dcc.Markdown(map_html)])]

if __name__ == '__main__':
    app.run_server(debug=True)
