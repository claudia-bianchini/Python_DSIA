import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

import folium
from branca.colormap import LinearColormap
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
import base64
import numpy as np

import os.path
from matplotlib import colors as mcols


# For the histogram
def devide_dataset(df):
    # Extract latitude and longitude
    latitudes = df['latitude']
    longitudes = df['longitude']

    # Calculate the most northern, southern, eastern, and western coordinates
    most_north = latitudes.max()
    most_south = latitudes.min()
    most_east = longitudes.min()
    most_west = longitudes.max()

    # Calculate average latitude and longitude
    average_lat = (most_north + most_south) / 2
    average_long = (most_east + most_west) / 2

    # Split the data into north and south regions based on latitude
    north_data = df[df['latitude'] <= average_lat]
    south_data = df[df['latitude'] > average_lat]


    # Split the data into north and south regions based on longitudes
    east_data = df[df['longitude'] >= average_long]
    west_data = df[df['longitude'] < average_long]

    return [north_data, south_data, east_data, west_data]

def plot_hist(north_TS_winter, south_TS_winter, east_TS_winter, west_TS_winter):
    # Common plot parameters
    common_plot_params = {
        'density': True,
        'bins': 100,
        'histtype': 'stepfilled'
    }

    # Create subplots for both histograms
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot the North vs South histogram
    axes[0].hist(north_TS_winter, label='North', color=mcols.to_rgba('tab:blue', 0.2), edgecolor='tab:blue', **common_plot_params)
    axes[0].hist(south_TS_winter, label='South', color=mcols.to_rgba('tab:orange', 0.2), edgecolor='tab:orange', **common_plot_params)
    axes[0].set_xlabel('TS')
    axes[0].set_ylabel('Events')
    axes[0].set_title('Year TS Variation in North vs South Regions WINTER')
    axes[0].legend(frameon=False, loc='upper left')

    # Plot the East vs West histogram
    axes[1].hist(east_TS_winter, label='East', color=mcols.to_rgba('tab:purple', 0.2), edgecolor='tab:purple', **common_plot_params)
    axes[1].hist(west_TS_winter, label='West', color=mcols.to_rgba('tab:olive', 0.2), edgecolor='tab:olive', **common_plot_params)
    axes[1].set_xlabel('TS')
    axes[1].set_ylabel('Events')
    axes[1].set_title('Year TS Variation in East vs West Regions WINTER')
    axes[1].legend(frameon=False, loc='upper left')

    # Adjust layout
    plt.tight_layout()




# For the map:
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


    # Map initialization:
    # Create a color scale
    color_dict = defaultdict(str)
    [color_dict, colormap] = color_scale(df, 'TS')
    
    # Histogram initialization
    df['year'] = df['year'].astype(str)
    
    # Devide dataset depending on the position of the measurment
    [north_data, south_data, east_data, west_data] = devide_dataset(df)

    # Groupby Each dataset for year
    north_data_year = north_data.groupby('year')
    south_data_year = south_data.groupby('year')
    east_data_year = east_data.groupby('year')
    west_data_year = west_data.groupby('year')

    # Extract the data we want to plot
    north_TS_winter = north_data_year.get_group('2004')[north_data_year.get_group('2004')['season'] == 'Winter']['TS']
    south_TS_winter = south_data_year.get_group('2004')[south_data_year.get_group('2004')['season'] == 'Winter']['TS']
    east_TS_winter = east_data_year.get_group('2004')[east_data_year.get_group('2004')['season'] == 'Winter']['TS']
    west_TS_winter = west_data_year.get_group('2004')[west_data_year.get_group('2004')['season'] == 'Winter']['TS']


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
        html.Iframe(id='map-iframe', width='100%', height='600'),

        html.Div([
        html.Img(src='data:image/png;base64,{}'.format(plot_hist(north_TS_winter, south_TS_winter, east_TS_winter, west_TS_winter)))
    ])
    ])

    @app.callback(
        Output('map-iframe', 'srcDoc'),
        Input('year-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('day-dropdown', 'value')
    )

    def update_map(selected_year, selected_month, selected_day):

        df['year'] = df['year'].astype(str)
        df['month'] = df['month'].astype(str) 
        df['day'] = df['day'].astype(str)

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

