import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

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


# Create a function to update the histograms
def update_histogram(selected_year, selected_season, selected_var, north_data_year, south_data_year, east_data_year, west_data_year):
    north_TS_winter = north_data_year.get_group(selected_year)[north_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    south_TS_winter = south_data_year.get_group(selected_year)[south_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    east_TS_winter = east_data_year.get_group(selected_year)[east_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    west_TS_winter = west_data_year.get_group(selected_year)[west_data_year.get_group(selected_year)['season'] == selected_season][selected_var]

    north_hist = px.histogram(x=north_TS_winter, title=f'North Region - {selected_var}')
    south_hist = px.histogram(x=south_TS_winter, title=f'South Region - {selected_var}')
    east_hist = px.histogram(x=east_TS_winter, title=f'East Region - {selected_var}')
    west_hist = px.histogram(x=west_TS_winter, title=f'West Region - {selected_var}')
    
    return north_hist, south_hist, east_hist, west_hist

def main():
    # Import data
    path_filtered_data = './output/filtered_data.csv'
    df = pd.read_csv(path_filtered_data)

    # Histogram initialization
    df['year'] = df['year'].astype(str)

    # Devide dataset depending on the position of the measurement
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

        dcc.Graph(id='north-hist'),
        dcc.Graph(id='south-hist'),
        dcc.Graph(id='east-hist'),
        dcc.Graph(id='west-hist')
    ])
    
    @app.callback(
        [Output('north-hist', 'figure'),
         Output('south-hist', 'figure'),
         Output('east-hist', 'figure'),
         Output('west-hist', 'figure')],
        [Input('year-dropdown', 'value'),
         Input('season-dropdown', 'value'),
         Input('var-dropdown', 'value')]
    )
    def update_graph(selected_year, selected_season, selected_var):
        # Implement your logic here to update histograms
        north_hist, south_hist, east_hist, west_hist = update_histogram(selected_year, selected_season, selected_var, north_data_year, south_data_year, east_data_year, west_data_year)
        return north_hist, south_hist, east_hist, west_hist

    if __name__ == '__main__':
        app.run_server(debug=True)

if __name__ == '__main__':
    main()