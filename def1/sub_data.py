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

def productivity_to_df(df, df_soja):
    # DROPPA COLONNE PRIMA DI FARE CIO'
    subdata_unique_name_year = df[['name_ibge', 'year', 'latitude', 'longitude']].drop_duplicates()
    # Merging dataframes
    subdata_unique_name_year = pd.merge(subdata_unique_name_year, df_soja, left_on='name_ibge', right_on='name', how='left')    
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

    return productivity_data
