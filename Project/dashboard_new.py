import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import folium
from branca.colormap import LinearColormap
from collections import defaultdict

# Define a function to create the map
def create_map(df, color_dict, colormap):
    if not df.empty:
        m = folium.Map(
            location=[df.iloc[1]['latitude'], df.iloc[1]['longitude']],
            zoom_start=7
        )

        for index, row in df.iterrows():
            unique_pair = (row['latitude'], row['longitude'])
            color = color_dict.get(unique_pair, 'blue')

            folium.CircleMarker(
                location=unique_pair,
                popup=f"Year: {row['year']}",
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.2,
                line_opacity=0.8,
            ).add_to(m)

        # Add the colormap to the map
        colormap.add_to(m)
        colormap.caption = f'Average Skin Earth temperature \'TS\' in [°C]'

        # Define a custom HTML legend
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; z-index:1000; background-color: white; padding: 10px; border: 1px solid grey;">
            <p><strong>Legend</strong></p>
            <p>CircleMarker Radius:</p>
            <p style="font-size: 12px;">Radius is proportional to Productivity.</p>
        </div>
        """

        # Add the custom HTML legend to the map
        m.get_root().html.add_child(folium.Element(legend_html))
        folium.map.LayerControl('topleft', collapsed=False).add_to(m)

    else:
        print("DataFrame is empty, cannot create the map.")

    return m


# Define the main function
def main():
    # Import data
    path_filtered_data = './output/filtered_data.csv'
    df = pd.read_csv(path_filtered_data)

    # Create a color scale
    color_dict = defaultdict(str)
    colormap = LinearColormap(['yellow', 'orange', 'red'], vmin=0, vmax=10)

    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Define the layout of the dashboard
    app.layout = html.Div([
        html.H1("Dashboard with Map"),

        # Dropdown to select a year
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in df['year'].unique()],
            value=df['year'].unique()[0]  # Initial value for the dropdown
        ),

        # Map component
        dcc.Graph(id='map')

        # Interval component for automatic updates
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # Update every 5 seconds
            n_intervals=0
        )
    ])

    # Callback to update the map based on the selected year
    @app.callback(
        Output('map', 'figure'),
        [Input('year-dropdown', 'value'), Input('interval-component', 'n_intervals')]
    )

    def update_map(selected_year):
        # Filter the dataset for the selected year
        selected_day = (n % df[df['year'] == selected_year]['day'].nunique()) + 1
        filtered_data = df[(df['year'] == selected_year)& (df['day'] == selected_day)]

        # Create the color scale for the selected year
        # You might need to adjust the color scale logic here based on your specific data and requirements

        color_dict = defaultdict(str)
        for index, row in filtered_data.iterrows():
            color = colormap(row['TS'])  # Assuming 'TS' is the temperature data in your DataFrame
            color_dict[(row['latitude'], row['longitude'])] = color

        subdata_unique_coord = filtered_data[['latitude', 'longitude']].drop_duplicates()

        # Create and return the map for the selected year
        return create_map(subdata_unique_coord, color_dict, colormap)

    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)


if __name__ == '__main__':
    main()


