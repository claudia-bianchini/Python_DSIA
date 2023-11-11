from collections import defaultdict
import warnings
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table
import pandas as pd
import folium
from branca.colormap import LinearColormap

import plotly.express as px
import plotly.graph_objects as go


import statsmodels.formula.api as smf

from statsmodels.tools.sm_exceptions import ConvergenceWarning

from sub_data import (
    find_normalized_productivity,
    normalize_values,
    divide_dataset,
    productivity_to_df
)

# Map functions
def generate_colormaps(df, variables):
    """
    Generate LinearColormap for numeric columns in the DataFrame.

    Args:
    - df (pd.DataFrame): The DataFrame containing the data.
    - variables (list): List of column names to consider.

    Returns:
    - dict: A dictionary containing LinearColormap objects for each numeric column.
    """
    colormaps = {}

    # Iterate through columns in the DataFrame
    for column in df.columns:
        # Check if the column is in the list of variables and has a numeric data type
        if column in variables and df[column].dtype in [int, float]:
            # Assuming numeric columns should have a LinearColormap
            colormaps[column] = LinearColormap(
                colors=['purple', 'blue', 'yellow', 'orange', 'red'],
                vmin=df[column].min(),
                vmax=df[column].max()
            )

    return colormaps



# Define a function to create the map
def create_map(df, color_dict, colormap, selected_var, variable_details):
    """
    Create a Folium map based on the provided DataFrame and color information.

    Args:
    - df (pd.DataFrame): The DataFrame containing geographical data.
    - color_dict (dict): Dictionary with unique coordinates as keys and associated colors as values.
    - colormap (LinearColormap): LinearColormap object representing the colors for the selected variable.
    - selected_var (str): The selected variable for color representation.
    - variable_details (dict): Details about the variables.

    Returns:
    - str: HTML representation of the Folium map.
    """
    print(f'create_map: ', df)
    if not df.empty:
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
        # Create a Folium map centered on the first location in the DataFrame
        m = folium.Map(
            location=[df.iloc[1]['latitude'], df.iloc[1]['longitude']],
            zoom_start=7
        )

        # Iterate through the DataFrame rows and add CircleMarker to the map
        for index, row in df.iterrows():
            unique_pair = (row['latitude'], row['longitude'])
            color = color_dict.get(unique_pair, 'green')

            folium.CircleMarker(
                location=unique_pair,
                popup=f"Name municìpios: {row['name_ibge']}",
                radius=row['productivity'],
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.2,
                line_opacity=0.8,
                weight=1
            ).add_to(m)

        # Add the colormap to the map
        colormap.add_to(m)
        colormap.caption = (
            f'{selected_var} [{variable_details[selected_var][1]}] '
            f'{variable_details[selected_var][0]}'
        )

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



def update_map(
    df, df_soja, selected_year, selected_month, selected_day, selected_var, variable_details, colormap
    ):
    """
    Update the Folium map based on selected options.

    Args:
    - df (pd.DataFrame): The DataFrame with geographical data.
    - df_soja (pd.DataFrame): The DataFrame with soybean data.
    - selected_year (str): Selected year.
    - selected_month (str): Selected month.
    - selected_day (str): Selected day.
    - selected_var (str): Selected variable for color representation.
    - variable_details (dict): Details about the variables.
    - colormap: LinearColormap object representing the colors for the selected variable.

    Returns:
    - str: HTML representation of the updated Folium map.
    """
    # Convert date-related columns to strings for filtering
    df['year'] = df['year'].astype(str)
    df['month'] = df['month'].astype(str)
    df['day'] = df['day'].astype(str)

    # Filter data based on selected date
    filtered_data = df[
        (df['year'] == selected_year) &
        (df['month'] == selected_month) &
        (df['day'] == selected_day)
    ]

    # Create a dictionary to store colors for filtered data
    color_dict_filtered = defaultdict(str)

    if not filtered_data.empty:
        # Populate color_dict_filtered with colors based on the selected variable
        for index, row in filtered_data.iterrows():
            color = colormap[selected_var](row[selected_var])
            color_dict_filtered[(row['latitude'], row['longitude'])] = color

        # Extract unique coordinates and normalize productivity
        subdata_unique_coord = filtered_data[
            ['name_ibge', 'latitude', 'longitude']
        ].drop_duplicates()
        subdata_unique_coord = find_normalized_productivity(
            subdata_unique_coord, 
            df_soja, selected_year
        )

        # Normalize productivity values to a specified range
        subdata_unique_coord['productivity'] = normalize_values(
            subdata_unique_coord['productivity'], 5, 15
        )  

        # Create the updated Folium map
        map_html = create_map(
            subdata_unique_coord, color_dict_filtered, colormap[selected_var], selected_var, variable_details
        )
    else:
        # Handle case where filtered data is empty
        empty_data = pd.DataFrame(columns=['latitude', 'longitude'])
        map_html = create_map(
            empty_data, color_dict_filtered, colormap[selected_var], selected_var, variable_details
        )

    return map_html


# Histograms functions
def update_histogram(
    selected_year, selected_season, selected_var, variable_details, north_data_year, south_data_year, east_data_year, west_data_year
):
    """
    Update the histograms based on selected options.

    Args:
    - selected_year (str): Selected year.
    - selected_season (str): Selected season.
    - selected_var (str): Selected variable for histogram representation.
    - variable_details (dict): Details about the variables.
    - north_data_year (pd.DataFrameGroupBy): Grouped data for North region.
    - south_data_year (pd.DataFrameGroupBy): Grouped data for South region.
    - east_data_year (pd.DataFrameGroupBy): Grouped data for East region.
    - west_data_year (pd.DataFrameGroupBy): Grouped data for West region.

    Returns:
    - tuple: Two Plotly figures representing North/South and East/West histograms.
    """
    # Create separate figures for North/South and East/West histograms
    fig_north_south = go.Figure()
    fig_east_west = go.Figure()

    # Define buttons for updating visibility in North/South histograms
    buttons_ns = [
        {'label': 'North - South', 'method': 'update', 'args': [{'visible': [True, True]}]},
        {'label': 'North', 'method':'update', 'args': [{'visible': [True, False]}]},
        {'label': 'South', 'method':'update', 'args': [{'visible': [False, True]}]},   
    ]

    # Define buttons for updating visibility in East/West histograms
    buttons_ew = [
        {'label' : 'East - West', 'method' : 'update', 'args' : [{'visible': [True, True]}]},
        {'label' : 'East', 'method' : 'update', 'args' : [{'visible': [True, False]}]},
        {'label' : 'West', 'method' : 'update', 'args' : [{'visible': [False, True]}]},    
    ]

    # Configure layout for North/South histogram
    fig_north_south.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                direction='down',
                buttons=buttons_ns,
                x=1.0,
                xanchor='right',
                y=1.15,
                yanchor='top'
            )
        ],
        title=f'North / South: Year {selected_year}, {selected_var} Variation in {selected_season}',
        xaxis_title=f'{selected_var} - {variable_details[selected_var][0]} [{variable_details[selected_var][1]}]',
        yaxis_title='Events'
    )

    # Configure layout for East/West histogram
    fig_east_west.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                direction='down',
                buttons=buttons_ew,
                x=1.0,
                xanchor='right',
                y=1.15,
                yanchor='top'
            )
        ],
        title=f'East / West: Year {selected_year}, {selected_var} Variation in {selected_season}',
        xaxis_title=f'{selected_var} - {variable_details[selected_var][0]} [{variable_details[selected_var][1]}]',
        yaxis_title='Events'
    )

    # Iterate over North/South and East/West data to create histograms
    for direction, data_year, fig in zip(['North', 'South'], [north_data_year, south_data_year], [fig_north_south, fig_north_south]):
        direction_var_season = data_year.get_group(selected_year)[data_year.get_group(selected_year)['season'] == selected_season][selected_var]

        # Assign color based on direction
        color = 'blue' if direction == 'North' else 'orange'

        # Configure bins and add histogram trace to the figure
        num_bins = 100
        bin_width = (max(direction_var_season) - min(direction_var_season)) / num_bins

        fig.add_trace(
            go.Histogram(
                x=direction_var_season,
                name=direction,
                marker_color=color,
                opacity=0.4,
                xbins=dict(start=min(direction_var_season), end=max(direction_var_season), size=bin_width)
            )
        )

    for direction, data_year, fig in zip(['East', 'West'], [east_data_year, west_data_year], [fig_east_west, fig_east_west]):
        direction_var_season = data_year.get_group(selected_year)[data_year.get_group(selected_year)['season'] == selected_season][selected_var]

        # Assign color based on direction
        color = 'green' if direction == 'East' else 'red'

        # Configure bins and add histogram trace to the figure
        num_bins = 100
        bin_width = (max(direction_var_season) - min(direction_var_season)) / num_bins
        bins = [i * bin_width + min(direction_var_season) for i in range(num_bins + 1)]

        fig.add_trace(
            go.Histogram(
                x=direction_var_season,
                name=direction,
                marker_color=color,
                opacity=0.4,
                xbins=dict(start=min(direction_var_season), end=max(direction_var_season), size=bin_width)
            )
        )

    return fig_north_south, fig_east_west



def update_lineplot(selected_var, variable_details, df, df_soja):
    """
    Update the line plot based on selected options.

    Args:
    - selected_var (str): Selected variable for line plot representation.
    - variable_details (dict): Details about the variables.
    - df (pd.DataFrame): The DataFrame containing data for the line plot.
    - df_soja (pd.DataFrame): The DataFrame containing soybean data.

    Returns:
    - plotly.graph_objects.Figure: Line plot figure.
    """
    # Calculate the sum for columns from the third position in df_soja
    year_productivity = {col: df_soja[col].sum() for col in df_soja.columns[3:]}

    # Calculate the mean of selected variable grouped by year and season
    mean_var = df.groupby(['year', 'season'])[selected_var].mean().reset_index()

    # Normalize productivity values between 0.1 and 1
    normalized_productivity = normalize_values(year_productivity, new_min=0.1, new_max=1)

    # Add the 'normalized_productivity' column to the 'mean_var' DataFrame
    mean_var['normalized_productivity'] = mean_var['year'].map(normalized_productivity)

    # Create a scatter plot with points colored by season and sized by normalized productivity
    scatter_fig = px.scatter(
        mean_var, 
        x='year', 
        y=selected_var, 
        color='season', 
        size='normalized_productivity',  # Use 'normalized_productivity' as size
        title=f'Mean {selected_var}[{variable_details[selected_var][1]}] - {variable_details[selected_var][0]} by Season for Each Year',
        labels={selected_var: selected_var}
    )

    # Create a line plot to connect the points
    line_fig = px.line(
        mean_var,
        x='year',
        y=selected_var,
        color='season',
        line_group='season',  # Grouping by season to connect points by season
        labels={selected_var: selected_var}
    )

    # Update traces in scatter plot and add line plot traces
    scatter_fig.update_traces()
    scatter_fig.add_traces(line_fig['data'])

    # Update layout with a dropdown menu for selecting seasons
    scatter_fig.update_layout(
        updatemenus=[
            {
                'buttons': [
                    {
                        'method': 'restyle',
                        'label': 'All Seasons',
                        'args': [{'visible': [True] * len(mean_var['season'].unique())}]
                    },
                    *[
                        {
                            'method': 'restyle',
                            'label': season,
                            'args': [
                                {'visible': [True if s == season else False for s in mean_var['season']]}
                            ]
                        } for season in mean_var['season'].unique()
                    ]
                ],
                'direction': 'down',
                'showactive': True,
            }
        ],
        height=500
    )
    return scatter_fig


def remove_outlier_indices(df):
    q_left = df.quantile(0.05)
    q_right = df.quantile(0.95)
    iqr = q_right - q_left
    true_list = ~((df < (q_left - 1.5 * iqr)) | (df > (q_right + 1.5 * iqr)))
    return true_list

def productivity_scatter_and_prediction(df, df_soja):
    """
    Create a scatter plot of productivity data and make predictions using a mixed-effects model.

    Args:
    - df (pd.DataFrame): The DataFrame containing productivity data.
    - df_soja (pd.DataFrame): The DataFrame containing soybean data.

    Returns:
    - tuple: A tuple containing:
        - plotly.graph_objects.Figure: Scatter plot figure.
        - pd.DataFrame: DataFrame containing predictions for each municipality.
    """
    # Prepare productivity data
    productivity_data = productivity_to_df(df, df_soja)
    
    # Remove outliers from the North region
    non_outlier_list_north = remove_outlier_indices(productivity_data['productivity'])
    productivity_data = productivity_data[non_outlier_list_north]

    # Filter data for training (years up to 2017) and prediction (years after 2017)
    max_prod_year = int(productivity_data['year'].max())
    prediction_data = pd.DataFrame({'year': [max_prod_year + 1, max_prod_year + 2, max_prod_year + 3]})

    # Ensure 'year' is treated as numeric
    productivity_data['year'] = pd.to_numeric(productivity_data['year'])
    prediction_data['year'] = pd.to_numeric(prediction_data['year'])

    # Dictionary to store predictions for each 'name_ibge'
    predictions_dict = {}

    # Iterate over unique 'name_ibge' values
    for name_ibge, group_data in productivity_data.groupby('name_ibge'):
        # Fit a mixed-effects model for each group
        md_north = smf.mixedlm("productivity ~ year", group_data, groups=group_data["name_ibge"], re_formula='~year')
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            mdf_north = md_north.fit(method=["powell"], maxiter=10000, start_params=[-231655.264, 100.0, 315929.301, 28.247, 282120.447])

        # Make predictions for every year in prediction_data
        group_prediction = mdf_north.predict(exog=prediction_data)
        # Store predictions in the dictionary
        predictions_dict[name_ibge] = pd.DataFrame({'year': prediction_data['year'], 'predictions': group_prediction})

    # Convert the dictionary to a DataFrame
    predictions_df = pd.concat(predictions_dict, names=['name_ibge']).reset_index()

    # Create a scatter plot with trendlines
    scatter_fig = px.scatter(
        productivity_data,
        x='year',
        y='productivity',
        color='name_ibge',
        trendline='ols',  # Ordinary Least Squares (OLS) trendline
        title="Productivity of Each Municipality Over Years",
        labels={'name_ibge': 'Municipality'}
    )

    # Update layout settings
    scatter_fig.update_layout(
        height=1000
    )

    return scatter_fig, predictions_df



def create_dash(df, df_soja):
    """
    Create a Dash application for visualizing agroclimatology data.

    Args:
    - df (pd.DataFrame): The main DataFrame.
    - df_soja (pd.DataFrame): Secondary DataFrame for additional processing.

    Returns:
    - dash.Dash: The created Dash application.
    """
    # Retrieve all column names
    all_columns = df.columns.tolist()
    
    # Columns to be removed
    columns_to_remove = ['codigo_ibge', 'latitude', 'longitude', 'year', 'month', 'day', 'season', 'name_ibge']
    
    # Create a list of variables starting from the column of a DataFrame deleting some of them
    variables = [col for col in all_columns if col not in columns_to_remove]
    
    variable_details = {
        'TS': ['Earth Skin Temperature', '°C'],
        'T2M': ['Temperature at 2 Meters', '°C'],
        'PS': ['Surface Pressure', 'kPa'],
        'GWETROOT': ['Root Zone Soil Wetness', '%'],
        'PRECTOTCORR': ['Precipitation Corrected', '??'],
        'ALLSKY_SFC_SW_DWN': ['All Sky Surface Shortwave Downward Irradiance', '??'],
        'CLRSKY_SFC_SW_DWN': ['Clear Sky Surface Shortwave Downward Irradiance', '??'],
        'WS2M': ['Wind Speed at 2 Meters', '??'],
        'WS10M': ['Wind Speed at 10 Meters', '??'],
    }
    
    # Create colormap and split dataset
    colormap = generate_colormaps(df, variables)
    [north_data, south_data, east_data, west_data] = divide_dataset(df)
    
    # Group by each dataset for the year
    north_data_year = north_data.groupby('year')
    south_data_year = south_data.groupby('year')
    east_data_year = east_data.groupby('year')
    west_data_year = west_data.groupby('year')

    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Static figure and table:
    intercept_fig, predictions_df = productivity_scatter_and_prediction(df, df_soja)
    # Convert DataFrame to a list of dictionaries for the DataTable
    data_table = [{'name_ibge': row['name_ibge'], 'year': row['year'], 'predictions': row['predictions']} for index, row in predictions_df.iterrows()]

    # Define the layout of the dashboard
    app.layout = html.Div([
        html.H1("Agroclimatology - Paranà (Brazil)", style={'text-align': 'center', 'color': 'green'}),  # Centered header

        html.Div([
            # Dropdowns for Year, Month, and Day
            html.Div([
                html.Label('Select Year:', style={'padding': '10px 0'}),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': year, 'value': year} for year in df['year'].unique()],
                    value=df['year'].min(),
                    style={'width': '200px'}  # Adjust the width of the dropdown
                )
            ], style={'display': 'inline-block', 'padding-right': '20px'}),  # Style for Year dropdown

            html.Div([
                html.Label('Select Month:', style={'padding': '10px 0'}),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[{'label': month, 'value': month} for month in df['month'].unique()],
                    value=df['month'].min(),
                    style={'width': '200px'}
                )
            ], style={'display': 'inline-block', 'padding-right': '20px'}),  # Style for Month dropdown

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
            html.Label('Select Variable:', style={'padding': '10px 0'}),
            dcc.Dropdown(
                id='var-dropdown',
                options=[
                    {'label': f'{var} - {variable_details[var][0]}', 'value': var, 'title': f'{var} - {variable_details[var][0]}'}
                    for var in variables
                ],
                value=variables[0],  # Initial value for the dropdown
                style={'width': '600px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center', 'padding-bottom': '20px'}),

        # Map component
        html.Iframe(id='map-iframe', width='100%', height='500'),

        # Dropdown for selecting the season
        html.Div([
            html.Label('Select Season:', style={'padding': '10px 0'}),
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': season, 'value': season} for season in df['season'].unique()],
                value='Winter',  # Initial value for the dropdown
                style={'width': '1000px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center', 'padding-bottom': '20px'}),

        # Histograms plot
        dcc.Graph(
            id='lat-hist',
            config={'displayModeBar': False}
        ),

        dcc.Graph(
            id='long-hist',
            config={'displayModeBar': False}
        ),

        # Lineplot
        dcc.Graph(
            id='line_years-plot',
            config={'displayModeBar': False}
        ),

        # Scatterplot
        dcc.Graph(
            id='scatter_prod-plot',
            figure=intercept_fig,
            config={'displayModeBar': False}
        ),

        # DataTable
        dash_table.DataTable(
            id='predictions-table',
            columns=[
                {'name': 'Name_IBGE', 'id': 'name_ibge', 'presentation': 'dropdown'},
                {'name': 'Year', 'id': 'year'},
                {'name': 'Predictions', 'id': 'predictions'},
            ],
            style_table={'height': '300px', 'overflowY': 'auto', 'width': '60%', 'margin': 'auto'},  # Set height and add scroll if needed
            data=data_table,
        ),

    ], style={'font-family': 'Arial, sans-serif', 'margin': '20px', 'background-color': 'white'})  # Define font-family and set margin for the entire layout

    # Update callback
    @app.callback(
        [Output('map-iframe', 'srcDoc'),
         Output('lat-hist', 'figure'),
         Output('long-hist', 'figure'),
         Output('line_years-plot', 'figure'),
         Output('scatter_prod-plot', 'figure'),
         Output('predictions-table', 'data')],
        [Input('year-dropdown', 'value'),
         Input('month-dropdown', 'value'),
         Input('day-dropdown', 'value'),
         Input('season-dropdown', 'value'),
         Input('var-dropdown', 'value')]
    )
    def update_map_and_graph(selected_year, selected_month, selected_day, selected_season, selected_var):
        # Map:
        map_html = update_map(df, df_soja, selected_year, selected_month, selected_day, selected_var, variable_details, colormap)

        # Histogram:
        fig_lat, fig_long = update_histogram(selected_year, selected_season, selected_var, variable_details, north_data_year, south_data_year, east_data_year, west_data_year)

        # Lineplot
        lineplot_fig_years = update_lineplot(selected_var, variable_details, df, df_soja)

        return map_html, fig_lat, fig_long, lineplot_fig_years, intercept_fig, data_table

    return app
