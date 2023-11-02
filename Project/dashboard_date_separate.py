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
        html.H1("Agroclimatology - Paranà (Brazil)"),

        # Dropdown for selecting the year
        html.Div([
            html.Label('Select Year:'),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in df['year'].unique()],
                value=df['year'].min()  # Initial value for the dropdown
            )
        ]),

        # Dropdown for selecting the month
        html.Div([
            html.Label('Select Month:'),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': month, 'value': month} for month in df['month'].unique()],
                value=df['month'].min()  # Initial value for the dropdown
            )
        ]),

        # Dropdown for selecting the day
        html.Div([
            html.Label('Select Day:'),
            dcc.Dropdown(
                id='day-dropdown',
                options=[{'label': day, 'value': day} for day in df['day'].unique()],
                value=df['day'].min()  # Initial value for the dropdown
            )
        ]),

        # Displaying the selected year, month, and day
        # html.Div(id='display-selected-day'),

        # Map component
        html.Iframe(id='map-iframe', width='100%', height='600')
    ])

    @app.callback(
        Output('map-iframe', 'srcDoc'),
        Input('year-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('day-dropdown', 'value')
    )

    def update_map(selected_year, selected_month, selected_day):

        df['year'] = df['year'].astype(int)
        df['month'] = df['month'].astype(int) 
        df['day'] = df['day'].astype(int)

        filtered_data = df[(df['year'] == selected_year) & (df['month'] == selected_month) & (df['day'] == selected_day)]
        
        if not filtered_data.empty:
            color_dict = defaultdict(str)
            for index, row in filtered_data.iterrows():
                color = colormap(row['TS'])  # Assuming 'TS' is the temperature data in your DataFrame
                color_dict[(row['latitude'], row['longitude'])] = color

            subdata_unique_coord = filtered_data[['name_ibge', 'latitude', 'longitude']].drop_duplicates()
            map_html = create_map(subdata_unique_coord, color_dict, colormap)
            print(type(map_html))
            return map_html

        else:
            empty_data = pd.DataFrame(columns=['latitude', 'longitude'])
            return create_map(empty_data, defaultdict(str), colormap)

    if __name__ == '__main__':
        app.run_server(debug=True)


if __name__ == '__main__':
    main()

