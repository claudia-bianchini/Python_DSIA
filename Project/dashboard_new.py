import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import folium
from branca.colormap import LinearColormap
from collections import defaultdict


# Define a colormap with a continuous scale of colors

def color_scale(dataframe, var):
    # Group the DataFrame by 'latitude' and 'longitude' and calculate the mean of 'var'
    #grouped_data = dataframe.groupby(['latitude', 'longitude'])[var].mean().reset_index()

    # Create a LinearColormap with colors 'yellow', 'orange', and 'red' based on the range of 'var' means
    colormap = LinearColormap(['purple', 'blue', 'yellow', 'orange', 'red'], vmin=dataframe[var].min(), vmax=dataframe[var].max())

    # Create a dictionary to store colors for each unique pair of 'latitude' and 'longitude'
    color_dict = defaultdict(str)
    for index, row in dataframe.iterrows():
        color = colormap(row[var])
        # Store the color as a string in the format 'rgb(xxx,xxx,xxx)'
        color_dict[(row['latitude'], row['longitude'])] = color

    return [color_dict, colormap]


# Define a function to create the map
def create_map(df, color_dict, colormap):
    if not df.empty:
        m = folium.Map(
            location=[df.iloc[1]['latitude'], df.iloc[1]['longitude']],
            zoom_start=7
        )

        for index, row in df.iterrows():
            unique_pair = (row['latitude'], row['longitude'])
            color = color_dict.get(unique_pair, 'green')

            folium.CircleMarker(
                location=unique_pair,
                popup=f"Name municìpios: {row['name_ibge']}",
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

    # Convert the Folium map to an HTML string
    map_html = m.get_root().render()
    # print(map_html)
    return map_html # [html.Div([dcc.Markdown(map_html)])]



# Define the main function
def main():
    # Import data
    path_filtered_data = './output/filtered_data.csv'
    df = pd.read_csv(path_filtered_data)

    # Create a color scale
    color_dict = defaultdict(str)
    [color_dict, colormap] = color_scale(df, 'TS')
    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Assuming df contains 'year', 'month', and 'day' columns
    years = df['year'].unique()
    months = df['month'].unique()
    days = df['day'].unique()
    # Define the layout of the dashboard
    app.layout = html.Div([
        html.H1("Dashboard with Map"),

        # Dropdown to select a year
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in df['year'].unique()],
            value=df['year'].min()  # Initial value for the dropdown
        ),

        # Displaying the selected year and current day
        html.Div(id='display-selected-year'),
        html.Div(id='display-selected-day'),

        # Interval component for automatic updates
        dcc.Interval(
            id='interval-component',
            interval=15 * 1000,  # Update every 15 seconds
            n_intervals=1
        ),

        # # Slider to select a month
        # dcc.Slider(
        #     id='month-slider',
        #     min=months.min(),
        #     max=months.max(),
        #     marks={str(month): str(month) for month in months},
        #     value=months.min(),  # Initial value for the slider
        #     step=1
        # ),

        # # Slider to select a day
        # dcc.Slider(
        #     id='day-slider',
        #     min=days.min(),
        #     max=days.max(),
        #     marks={str(day): str(day) for day in days},
        #     value=days.min(),  # Initial value for the slider
        #     step=1
        # ),

        # Map component
        html.Iframe(id='map-iframe', width='100%', height='600')
        # dcc.Graph(id='map'),
    ])

    # Callback to update the map based on the selected year
    @app.callback(
        Output('map-iframe', 'srcDoc'),
        [Input('year-dropdown', 'value'), Input('interval-component', 'n_intervals')]
    )
    
    def update_map(selected_year, n):
        # Convert the 'Your_Column' column from string to integer
        df['year'] = df['year'].astype(int)
        df['day'] = df['day'].astype(int)
        # Calculate the current day based on the interval counter
        filtered_data = df[(df['year'] == selected_year)] # & (df['day'] == n % df['day'].nunique() + 1)]
        print(filtered_data)
        # Get the selected year from the callback context
        # year = dash.callback_context.triggered[0]['prop_id'].split('.')[0] 
        if not filtered_data.empty:
            # Create the color scale for the selected year
            color_dict = defaultdict(str)
            for index, row in filtered_data.iterrows():
                color = colormap(row['TS'])  # Assuming 'TS' is the temperature data in your DataFrame
                color_dict[(row['latitude'], row['longitude'])] = color

            subdata_unique_coord = filtered_data[['name_ibge', 'latitude', 'longitude']].drop_duplicates()
            #print(len(subdata_unique_coord))
            # Create and return the map for the selected year
            return create_map(subdata_unique_coord, color_dict, colormap)

        else:
            # If the filtered data is empty, return an empty map
            empty_data = pd.DataFrame(columns=['latitude', 'longitude'])
            print('filterd data empty')
            return create_map(empty_data, defaultdict(str), colormap)

    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)


if __name__ == '__main__':
    main()


