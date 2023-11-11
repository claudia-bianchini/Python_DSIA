import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import io
import base64
import plotly.graph_objects as go
from matplotlib import colors as mcols


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

def main():
    # Import data
    path_filtered_data = './output/filtered_data.csv'
    df = pd.read_csv(path_filtered_data)

    # Histogram initialization
    df['year'] = df['year'].astype(str)

    # Divide dataset depending on the position of the measurement
    [north_data, south_data, east_data, west_data] = devide_dataset(df)

    # Groupby each dataset for the year
    north_data_year = north_data.groupby('year')
    south_data_year = south_data.groupby('year')
    east_data_year = east_data.groupby('year')
    west_data_year = west_data.groupby('year')

    # Retrieve all column names
    all_columns = df.columns.tolist()

    # Columns to be removed
    columns_to_remove = ['codigo_ibge', 'latitude', 'longitude', 'year', 'month', 'day', 'season', 'name_ibge']

    # Create a list of variables starting from the column of a DataFrame deleting some of them
    variables = [col for col in all_columns if col not in columns_to_remove]


    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Histograms for Different Regions"),

        # Dropdown for selecting the year
        html.Div([
            html.Label('Select Year:'),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in df['year'].unique()],
                value=df['year'].min()  # Initial value for the dropdown
            )
        ]),

        # Dropdown for selecting the season
        html.Div([
            html.Label('Select Season:'),
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': season, 'value': season} for season in df['season'].unique()],
                value='Winter'  # Initial value for the dropdown
            )
        ]),

        # Dropdown for selecting variable
        html.Div([
            html.Label('Select Varible:'),
            dcc.Dropdown(
                id='var-dropdown',
                options=[{'label': var, 'value': var} for var in variables],
                value= variables[0]  # Initial value for the dropdown
            )
        ]),

        dcc.Graph(
            id='north-hist',
            config={'displayModeBar': False}
        ),
        dcc.Graph(
            id='east-hist',
            config={'displayModeBar': False}
        ),
    ])
    
    @app.callback(
        [Output('north-hist', 'figure'),
         Output('east-hist', 'figure')],
        [Input('year-dropdown', 'value'),
         Input('season-dropdown', 'value'),
         Input('var-dropdown', 'value')]
    )
    def update_graph(selected_year, selected_season, selected_var):
        fig_NS, fig_EW = update_histogram(selected_year, selected_season, selected_var, north_data_year, south_data_year, east_data_year, west_data_year)

        return fig_NS, fig_EW

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False)

if __name__ == '__main__':
    main()
