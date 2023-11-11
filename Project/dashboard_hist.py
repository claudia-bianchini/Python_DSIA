import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib import colors as mcols
import io
import base64
import plotly.graph_objects as go 

import matplotlib
matplotlib.use('Agg') 

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


def convert_fig_to_plotly_image(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


# Create a function to update the histograms
def update_histogram(selected_year, selected_season, selected_var, north_data_year, south_data_year, east_data_year, west_data_year):
    north_var_season = north_data_year.get_group(selected_year)[north_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    south_var_season = south_data_year.get_group(selected_year)[south_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    east_var_season = east_data_year.get_group(selected_year)[east_data_year.get_group(selected_year)['season'] == selected_season][selected_var]
    west_var_season = west_data_year.get_group(selected_year)[west_data_year.get_group(selected_year)['season'] == selected_season][selected_var]


    # Common plot parameters
    common_plot_params = {
        'density': True,
        'bins': 100,
        'histtype': 'stepfilled'
    }

    # Create subplots for both histograms
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Create a figure for North-South histogram
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.hist(north_var_season, label='North', color=mcols.to_rgba('tab:blue', 0.2), edgecolor='tab:blue', **common_plot_params)
    ax1.hist(south_var_season, label='South', color=mcols.to_rgba('tab:orange', 0.2), edgecolor='tab:orange', **common_plot_params)
    ax1.set_xlabel(f'{selected_var}', fontsize=14)
    ax1.set_ylabel('Events', fontsize=14)
    ax1.set_title(f'Year {selected_year}: {selected_var} Variation in North vs South Regions {selected_season}', fontsize=16)
    ax1.legend(frameon=False, loc='upper left')

    # Create a figure for East-West histogram
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.hist(east_var_season, label='East', color=mcols.to_rgba('tab:purple', 0.2), edgecolor='tab:purple', **common_plot_params)
    ax2.hist(west_var_season, label='West', color=mcols.to_rgba('tab:olive', 0.2), edgecolor='tab:olive', **common_plot_params)
    ax2.set_xlabel(f'{selected_var}', fontsize=14)
    ax2.set_ylabel('Events', fontsize=14)
    ax2.set_title(f'Year {selected_year}: {selected_var} Variation in East vs West Regions {selected_season}', fontsize=16)
    ax2.legend(frameon=False, loc='upper left')

    # Adjust layout
    plt.tight_layout()
    # Convert Matplotlib figures to Plotly-compatible base64-encoded images
    img1 = convert_fig_to_plotly_image(fig1)
    img2 = convert_fig_to_plotly_image(fig2)
    
    return img1, img2

def main():
    # Import data
    path_filtered_data = './output/filtered_data.csv'
    df = pd.read_csv(path_filtered_data)

    # Histogram initialization
    df['year'] = df['year'].astype(str)

    # Devide dataset depending on the position of the measurement
    [north_data, south_data, east_data, west_data] = divide_dataset(df)

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
            config={'displayModeBar': False} ),
        # dcc.Graph(id='south-hist'),
        dcc.Graph(
            id='east-hist',
            config={'displayModeBar': False} ),
        # dcc.Graph(id='west-hist')
    ])
    
    @app.callback(
        [Output('north-hist', 'figure'),
        Output('east-hist', 'figure')],
        [Input('year-dropdown', 'value'),
         Input('season-dropdown', 'value'),
         Input('var-dropdown', 'value')]
    )
    def update_graph(selected_year, selected_season, selected_var):
        plotly_img_NS, plotly_img_EW = update_histogram(selected_year, selected_season, selected_var, north_data_year, south_data_year, east_data_year, west_data_year)

        # Create Plotly figures using the base64-encoded images
        plotly_fig_NS = go.Figure(go.Image(source=plotly_img_NS))
        plotly_fig_EW = go.Figure(go.Image(source=plotly_img_EW))


        return plotly_fig_NS, plotly_fig_EW 

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False)

if __name__ == '__main__':
    main()