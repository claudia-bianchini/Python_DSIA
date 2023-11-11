import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table
from dash.dash_table.Format import Group
import pandas as pd
import folium
from branca.colormap import LinearColormap
from collections import defaultdict
import plotly.express as px
import io
import base64
import plotly.graph_objects as go


import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf


import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning


from plotly.subplots import make_subplots

# Map functions
def generate_colormaps(df, variables):
    """
    Generate LinearColormap for numeric columns in the DataFrame.

    Args:
    - df (pd.DataFrame): The DataFrame.
    - variables (list): List of column names.

    Returns:
    - dict: A dictionary containing LinearColormap objects for each numeric column.
    """
    colormaps = {}
    for column in df.columns:
        if column in variables and df[column].dtype in [int, float]:
            # Assuming numeric columns should have a LinearColormap
            colormaps[column] = LinearColormap(['purple', 'blue', 'yellow', 'orange', 'red'], vmin=df[column].min(), vmax=df[column].max())
    return colormaps

def find_normalized_productivity(sub_data_unique_coord, df_soja, selected_year):
    # Check if 'name_ibge' column exists in sub_data_unique_coord and 'name' column exists in df_soja
    if 'name_ibge' in sub_data_unique_coord.columns and 'name' in df_soja.columns:
        # Merge the dataframes based on the condition name_ibge == name
        merged_df = sub_data_unique_coord.merge(df_soja[['name', selected_year]], left_on='name_ibge', right_on='name', how='left')

        # Rename the selected_year column to a unique name (avoid name conflicts)
        merged_df = merged_df.rename(columns={selected_year: 'productivity'})

        # Return the updated DataFrame
        return merged_df
    else:
        # If 'name_ibge' or 'name' columns don't exist in respective DataFrames
        print("'name_ibge' column not found in sub_data_unique_coord or 'name' column not found in df_soja.")
        return sub_data_unique_coord  # Return the original DataFrame



def normalize_values(data, new_min, new_max):
    # Stampa le somme dei valori per ciascuna colonna
    all_values = []
    for key, value in data.items():
        all_values.append(value)

    min_val = min(all_values)
    max_val = max(all_values)
    
    normalized = {}
    for key, value in data.items():
        normalized_value = new_min + (value - min_val) * (new_max - new_min) / (max_val - min_val)
        normalized[key] = normalized_value

    return normalized

# Define a function to create the map
def create_map(df, color_dict, colormap, selected_var, variable_details):
    """
    Create a Folium map based on the provided DataFrame and color information.

    Args:
    - df (pd.DataFrame): The DataFrame containing geographical data.
    - color_dict (dict): Dictionary with unique coordinates as keys and associated colors as values.
    - colormap: LinearColormap object representing the colors for the selected variable.
    - selected_var (str): The selected variable for color representation.
    - variable_details (dict): Details about the variables.

    Returns:
    - str: HTML representation of the Folium map.
    """

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
                radius= row['productivity'],
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.2,
                line_opacity=0.8,
                weight = 1
            ).add_to(m)

        # Add the colormap to the map
        colormap.add_to(m)
        colormap.caption = f'{selected_var} '#- {variable_details[selected_var][0]} [{variable_details[selected_var][1]}]'

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
    

def update_map(df, df_soja, selected_year, selected_month, selected_day, selected_var, variable_details, colormap):
    """
    Update the Folium map based on selected options.

    Args:
    - df (pd.DataFrame): The DataFrame with geographical data.
    - selected_year (str): Selected year.
    - selected_month (str): Selected month.
    - selected_day (str): Selected day.
    - selected_var (str): Selected variable for color representation.
    - variable_details (dict): Details about the variables.
    - colormap: LinearColormap object representing the colors for the selected variable.

    Returns:
    - str: HTML representation of the updated Folium map.
    """
    df['year'] = df['year'].astype(str)
    df['month'] = df['month'].astype(str)
    df['day'] = df['day'].astype(str)

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
        subdata_unique_coord = find_normalized_productivity(subdata_unique_coord, df_soja, selected_year)
        subdata_unique_coord['productivity'] = normalize_values(subdata_unique_coord['productivity'], 5, 15)   # now the column has normalized values
        map_html = create_map(subdata_unique_coord, color_dict_filtered, colormap[selected_var], selected_var, variable_details)

    else:
        empty_data = pd.DataFrame(columns=['latitude', 'longitude'])
        map_html = create_map(empty_data, color_dict_filtered, colormap[selected_var], selected_var, variable_details)

    return map_html

# Histograms functions
def divide_dataset(df):
    """
    Divide the dataset into north, south, east, and west regions based on coordinates.

    Args:
    - df (pd.DataFrame): The DataFrame with geographical data.

    Returns:
    - list: List of DataFrames for north, south, east, and west regions.
    """
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


def update_histogram(selected_year, selected_season, selected_var, variable_details, north_data_year, south_data_year, east_data_year, west_data_year):
    fig_north_south = go.Figure()
    fig_east_west = go.Figure()

    buttons_ns = [
        dict(label='Nort - South', method='update', args=[{'visible': [True, True]}]),
        dict(label='North', method='update', args=[{'visible': [True, False]}]),
        dict(label='South', method='update', args=[{'visible': [False, True]}]),   
    ]

    buttons_ew = [
        dict(label='East - West', method='update', args=[{'visible': [True, True]}]),
        dict(label='East', method='update', args=[{'visible': [True, False]}]),
        dict(label='West', method='update', args=[{'visible': [False, True]}]),    
    ]

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

    for direction, data_year, fig in zip(['North', 'South'], [north_data_year, south_data_year], [fig_north_south, fig_north_south]):
        direction_var_season = data_year.get_group(selected_year)[data_year.get_group(selected_year)['season'] == selected_season][selected_var]

        color = 'blue' if direction == 'North' else 'orange'

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

    for direction, data_year, fig in zip(['East', 'West'], [east_data_year, west_data_year], [fig_east_west, fig_east_west]):
        direction_var_season = data_year.get_group(selected_year)[data_year.get_group(selected_year)['season'] == selected_season][selected_var]

        color = 'green' if direction == 'East' else 'red'

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

    # Calculate the sum for columns from the third position
    year_productivity = {col: df_soja[col].sum() for col in df_soja.columns[3:]}

    
    mean_var = df.groupby(['year', 'season'])[selected_var].mean().reset_index()
    
    # Normalize productivity values between 1 and 3
    normalized_productivity = normalize_values(year_productivity, new_min=0.1, new_max=1)

    # Aggiunta della colonna 'normalized_productivity' al DataFrame 'mean_var'
    mean_var['normalized_productivity'] = mean_var['year'].map(normalized_productivity)

    scatter_fig = px.scatter(
        mean_var, 
        x='year', 
        y=selected_var, 
        color='season', 
        size= 'normalized_productivity',  # Utilizza la colonna 'normalized_productivity' come dimensione
        title=f'Mean {selected_var}[{variable_details[selected_var][1]}] - {variable_details[selected_var][0]}  by Season for Each Year',
        labels={selected_var: selected_var}#'Productivity'}# 'normalized_productivity': 'Normalized Productivity'}
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
    scatter_fig.update_traces()
    scatter_fig.add_traces(line_fig['data']) 
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



def productivity_to_df(df, df_soja):
    # DROPPA COLONNE PRIMA DI FARE CIO'
    #print(df.columns)
    subdata_unique_name_year = df[['name_ibge', 'year', 'latitude', 'longitude']].drop_duplicates()
    # print(f'subdata_unique_name_year = ', subdata_unique_name_year)
    #print(df_soja)
    # Merging dataframes
    subdata_unique_name_year = pd.merge(subdata_unique_name_year, df_soja, left_on='name_ibge', right_on='name', how='left')
     # for row in merged_df.itertuples():
    #     if str(row.year) in merged_df.columns:
    #         df.at[row.Index, 'productivity'] = merged_df.at[row.Index, str(row.year)]

    
    # Filter out the columns from 'df_soja' that contain the numeric values
    year_columns = df_soja.columns[3:]
    # print(year_columns)
    # Create an empty list to store productivity values
    productivity_data = pd.DataFrame(columns = ['name_ibge', 'latitude', 'longitude', 'year','productivity'])
    # Iterate through the merged dataframe and check for matches
    for index, row in subdata_unique_name_year.iterrows():
        for col in year_columns:
            # print(row['year'], row[col])
            # print(type(row['year']), type(row[col]))
            if row['year'] == col:
                productivity_data.loc[index] = [row['name_ibge'], row['latitude'], row['longitude'], row['year'], row[col]]

    # Assign the obtained productivity values to the 'productivity' column in 'df'
    #subdata_unique_name_year['productivity'] = productivity_values

    print(f'prod-val: {productivity_data}')
    return productivity_data



def Remove_Outlier_Indices(df):
    Q01 = df.quantile(0.25)
    Q09 = df.quantile(0.75)
    IQR = Q09 - Q01
    trueList = ~((df < (Q01 - 1.5 * IQR)) |(df > (Q09 + 1.5 * IQR)))
    return trueList



# NON è UN GRAFICO DINAMICO!Togli da dinamicità
def update_lineplot2(df, df_soja):
    #print(f'north data: ', north_data)
    north_data = df
    # Drow two plot, you can select if you want to see north-south or west-east
    productivity_data = productivity_to_df(df, df_soja)
    # Index List of Non-Outliers
    nonOutlierList_north = Remove_Outlier_Indices(productivity_data['productivity'])
    # Non-Outlier Subset of the Given Dataset
    productivity_data = productivity_data[nonOutlierList_north]

    # Filter data for training (years up to 2017) and prediction (years after 2017)
    prediction_data = pd.DataFrame({'year': [2018, 2019, 2020]})

    # Ensure 'year' is treated as numeric
    productivity_data['year'] = pd.to_numeric(productivity_data['year'])
    prediction_data['year'] = pd.to_numeric(prediction_data['year'])

    # Dictionary to store predictions for each 'name_ibge'
    predictions_dict = {}

    # Iterate over unique 'name_ibge' values
    for name_ibge, group_data in productivity_data.groupby('name_ibge'):
        # Fit a model for each group
        md_north = smf.mixedlm("productivity ~ year", group_data, groups=group_data["name_ibge"], re_formula='~year')
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            mdf_north = md_north.fit(method=["powell"], maxiter=10000, start_params=[-231655.264, 100.0, 315929.301, 28.247, 282120.447])

        #print(mdf_north.summary())
        # Make predictions for every year in prediction_data
        group_prediction = mdf_north.predict(exog=prediction_data)
        # Store predictions in the dictionary
        predictions_dict[name_ibge] = pd.DataFrame({'year': prediction_data['year'], 'predictions': group_prediction})

    # Convert the dictionary to a DataFrame
    # predictions_df = pd.concat(predictions_dict, names=['name_ibge']).reset_index()
    predictions_df = pd.concat(predictions_dict, names=['name_ibge']).reset_index()
    # predictions_df.columns = ['name_ibge', 'year', 'prediction']

    # Print the predictions DataFrame
    print(predictions_df)

    scatter_fig = px.scatter(
        productivity_data,
        x='year',
        y='productivity',
        color='name_ibge',
        trendline='ols',
        title=f"Productivity of each municipal over years",
        labels= 'name_ibge'
    )

    # scatter_fig.update_traces()
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
        'PS' : ['Surface Preassure', '??'],
        'GWETROOT': ['Root Zone Soil Wetness','%'],
        #'Precipitation': 'mm',
        #'Wind_Speed': 'm/s',
        
    }
    
    # Create colormap and split dataset
    colormap = generate_colormaps(df, variables)
    # Divide dataset depending on the position of the measurement
    [north_data, south_data, east_data, west_data] = divide_dataset(df)
    # print(f'north_data : ', len(north_data))    #north_data :  777328
    # print(f'south_data : ', len(south_data))    # south_data :  1007458
    # print(f'east_data : ', len(east_data))  # east_data :  772214
    # print(f'west_data : ', len(west_data))   # west_data :  1012572
    # # Groupby each dataset for the year
    north_data_year = north_data.groupby('year') 
    south_data_year = south_data.groupby('year') 
    east_data_year = east_data.groupby('year')
    west_data_year = west_data.groupby('year')
    #print(f'df = {df}')
    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Static figure and table:
    intercept_fig, predictions_df = update_lineplot2(df, df_soja)
    print(type(predictions_df))
    # data_table = [{'name_ibge': key, 'year': value[0], 'prediction': value[1]} for key, value in predictions_df.items()]
    data_table = [{'name_ibge': row['name_ibge'], 'year': row['year'], 'predictions': row['predictions']} for index, row in predictions_df.iterrows()]

    # Define the layout of the dashboard
    app.layout = html.Div([
        html.H1("Agroclimatology - Paranà (Brazil)", style={'text-align': 'center', 'color': 'green'}),  # Centered header

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
                #options=[{'label': var, 'value': var} for var in variables],
                options=[
                    {'label': f'{var} - {variable_details[var][0]}', 'value': var, 'title': f'{var} - {variable_details[var][0]}'}
                    for var in variables
                ],
                value= variables[0],  # Initial value for the dropdown
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
            # figure = fig_lat,
            config={'displayModeBar': False}
        ),

        dcc.Graph(
            id='long-hist',
            # figure = fig_long,
            config={'displayModeBar': False}
        ),

        # Lineplot
        dcc.Graph(
            id='line_years-plot',
            #figure = lineplot_fig_years,
            config={'displayModeBar': False}
        ), 

        # Scatterplot
        dcc.Graph(
            id='scatter_prod-plot',
            figure = intercept_fig,
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
            # Add the data from your DataFrame
            data=data_table,
        )], style={'font-family': 'Arial, sans-serif', 'margin': '20px','background-color': 'white'})  # Define font-family and set margin for the entire layout
        
    
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
         Input('var-dropdown', 'value'),]
    )

    
    def update_map_and_graph(selected_year, selected_month, selected_day, selected_season, selected_var): 
        # Map:
        map_html = update_map(df, df_soja, selected_year, selected_month, selected_day, selected_var, variable_details, colormap)
        
        # Histogram:
        fig_lat, fig_long= update_histogram(selected_year, selected_season, selected_var, variable_details, north_data_year, south_data_year, east_data_year, west_data_year)
        
        # Lineplot
        lineplot_fig_years = update_lineplot(selected_var, variable_details, df, df_soja)
        
        return map_html, fig_lat, fig_long, lineplot_fig_years, intercept_fig, data_table
    
    return app
    


