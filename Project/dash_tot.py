import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import folium
from branca.colormap import LinearColormap
from collections import defaultdict
import plotly.express as px
import io
import base64
import plotly.graph_objects as go

# Map functions
def generate_colormaps(df, variables):
    colormaps = {}
    for column in df.columns:
        if column in variables and df[column].dtype in [int, float]:
            # Assuming numeric columns should have a LinearColormap
            colormaps[column] = LinearColormap(['purple', 'blue', 'yellow', 'orange', 'red'], vmin=df[column].min(), vmax=df[column].max())
    return colormaps


# Define a function to create the map
def create_map(df, color_dict, colormap, selected_var):
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
        colormap.caption = f'{selected_var} range'

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

        # Convert the Folium map to an HTML string
        map_html = m.get_root().render()
        return map_html 
    else:
        print("DataFrame is empty, cannot create the map.")
        return None
    

def update_map(df, selected_year, selected_month, selected_day, selected_var, colormap):
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    df['day'] = df['day'].astype(int)

    filtered_data = df[
        (df['year'] == selected_year) &
        (df['month'] == selected_month) &
        (df['day'] == selected_day)
    ]

    color_dict_filtered = defaultdict(str)
    if not filtered_data.empty:
        for index, row in filtered_data.iterrows():
            color = colormap[selected_var](row[selected_var])
            color_dict_filtered[(row['latitude'], row['longitude'])] = color

        subdata_unique_coord = filtered_data[['name_ibge', 'latitude', 'longitude']].drop_duplicates()
        map_html = create_map(subdata_unique_coord, color_dict_filtered, colormap[selected_var], selected_var)

    else:
        empty_data = pd.DataFrame(columns=['latitude', 'longitude'])
        map_html = create_map(empty_data, color_dict_filtered, colormap[selected_var], selected_var)

    return map_html

# Histograms functions
def divide_dataset(df):
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

def update_histogram(selected_year, selected_season, selected_var, north_data_year, south_data_year, east_data_year, west_data_year):
    north_var_season = north_data_year.get_group(selected_year)[north_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    south_var_season = south_data_year.get_group(selected_year)[south_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    east_var_season = east_data_year.get_group(selected_year)[east_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    west_var_season = west_data_year.get_group(selected_year)[west_data_year.get_group(selected_year)['season'] == selected_season][selected_var]

    # Create histograms using Plotly graph objects
    fig_NS = go.Figure()
    fig_NS.add_trace(go.Histogram(x=north_var_season, name='North', marker_color = 'rgba(100, 0, 0, 0.5)', opacity = 0.6))
    fig_NS.add_trace(go.Histogram(x=south_var_season, name='South', marker_color = 'rgba(0, 100, 0, 0.5)', opacity = 0.6))

    fig_NS.update_layout(barmode='overlay', title=f'Year {selected_year}: {selected_var} Variation in North vs South Regions {selected_season}', xaxis_title=selected_var, yaxis_title='Events')

    fig_EW = go.Figure()
    fig_EW.add_trace(go.Histogram(x=east_var_season, name='East', marker_color='rgba(100, 0, 0, 0.5)', opacity = 0.6))
    fig_EW.add_trace(go.Histogram(x=west_var_season, name='West', marker_color='rgba(0, 100, 0, 0.5)', opacity = 0.6))

    fig_EW.update_layout(barmode='overlay', title=f'Year {selected_year}: {selected_var} Variation in East vs West Regions {selected_season}', xaxis_title=selected_var, yaxis_title='Events')

    return fig_NS, fig_EW

# ... (Previous code)

def main():
    # Precompute colormap and initial dataset split outside the app
    path_filtered_data = './output/filtered_data.csv'
    df = pd.read_csv(path_filtered_data)

    # Retrieve all column names
    all_columns = df.columns.tolist()
    # Columns to be removed
    columns_to_remove = ['codigo_ibge', 'latitude', 'longitude', 'year', 'month', 'day', 'season', 'name_ibge']
    # Create a list of variables starting from the column of a DataFrame deleting some of them
    variables = [col for col in all_columns if col not in columns_to_remove]

    # Create colormap and split dataset
    colormap = generate_colormaps(df, variables)
    north_data, south_data, east_data, west_data = divide_dataset(df)

    # Divide dataset depending on the position of the measurement
    [north_data, south_data, east_data, west_data] = divide_dataset(df)

    # Groupby each dataset for the year
    north_data_year = north_data.groupby('year')
    south_data_year = south_data.groupby('year')
    east_data_year = east_data.groupby('year')
    west_data_year = west_data.groupby('year')

    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Define the layout of the dashboard
    app.layout = html.Div([
        html.H1("Agroclimatology - Paranà (Brazil)", style={'text-align': 'center'}),  # Centered header

       html.Div([
        # Dropdown for Year
        html.Div([
            html.Label('Select Year:', style={'padding': '10px 0'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in df['year'].unique()],
                value=df['year'].min(),
                style={'width': '200px'}  # Adjust the width of the dropdown
            )
        ], style={'display': 'inline-block', 'padding-right': '20px'}),  # Style for Year dropdown

        # Dropdown for Month
        html.Div([
            html.Label('Select Month:', style={'padding': '10px 0'}),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': month, 'value': month} for month in df['month'].unique()],
                value=df['month'].min(),
                style={'width': '200px'}
            )
        ], style={'display': 'inline-block', 'padding-right': '20px'}),  # Style for Month dropdown

        # Dropdown for Day
        html.Div([
            html.Label('Select Day:', style={'padding': '10px 0'}),
            dcc.Dropdown(
                id='day-dropdown',
                options=[{'label': day, 'value': day} for day in df['day'].unique()],
                value=df['day'].min(),
                style={'width': '200px'}
            )
        ], style={'display': 'inline-block'})  # Style for Day dropdown
    ], style={'text-align': 'center', 'padding-bottom': '20px'}),  # Center the dropdowns and set padding
        
        # Dropdown for selecting variable
        html.Div([
            html.Label('Select Varible:', style={'padding': '10px 0'}),
            dcc.Dropdown(
                id='var-dropdown',
                options=[{'label': var, 'value': var} for var in variables],
                value= variables[0],  # Initial value for the dropdown
                style={'width': '200px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center'}),

        # Map component
        html.Iframe(id='map-iframe', width='100%', height='600'),

        
        # Dropdown for selecting the season
        html.Div([
            html.Label('Select Season:', style={'padding': '10px 0'}),
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': season, 'value': season} for season in df['season'].unique()],
                value='Winter',  # Initial value for the dropdown
                style={'width': '200px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center'}),

        

        dcc.Graph(
            id='north-hist',
            config={'displayModeBar': False}
        ),
        dcc.Graph(
            id='east-hist',
            config={'displayModeBar': False}
        ),
    ], style={'font-family': 'Arial, sans-serif', 'margin': '20px'})  # Define font-family and set margin for the entire layout

    # Update callback
    @app.callback(
        [Output('map-iframe', 'srcDoc'),
         Output('north-hist', 'figure'),
         Output('east-hist', 'figure')],
        [Input('year-dropdown', 'value'),
         Input('month-dropdown', 'value'),
         Input('day-dropdown', 'value'),
         Input('season-dropdown', 'value'),
         Input('var-dropdown', 'value')]
    )
    def update_map_and_graph(selected_year, selected_month, selected_day, selected_season, selected_var):
        # Map:
        map_html = update_map(df, selected_year, selected_month, selected_day, selected_var, colormap)
        
        # Histogram:
        fig_NS, fig_EW = update_histogram(selected_year, selected_season, selected_var, north_data_year, south_data_year, east_data_year, west_data_year)
        
        return map_html, fig_NS, fig_EW
    
    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)

if __name__ == '__main__':
    main()
