"""
Module Description:
This module contains functions for data normalization, dataset division based on coordinates,
and extracting structured productivity data from given DataFrames. Additionally, it provides a function
for creating a normalized productivity DataFrame for a selected year.

Functions:
- find_normalized_productivity(sub_data_unique_coord, df_soja, selected_year)
- normalize_values(data, new_min, new_max)
- divide_dataset(df)
- productivity_to_df(df, df_soja)
"""

import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import folium
from branca.colormap import LinearColormap
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from plotly.subplots import make_subplots


def find_normalized_productivity(sub_data_unique_coord, df_soja, selected_year):
    """
    Find and normalize productivity values for a selected year.

    Args:
        sub_data_unique_coord (pd.DataFrame): DataFrame containing unique coordinates and 'name_ibge' column.
        df_soja (pd.DataFrame): DataFrame containing 'name' column and productivity values for various years.
        selected_year (str): The selected year for which productivity values need to be normalized.

    Returns:
        pd.DataFrame: Merged DataFrame containing normalized productivity values for the selected year.
    """
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
    """
    Normalize values in a dictionary to a specified range.

    Args:
        data (dict): Dictionary with keys as column names and values as the original data.
        new_min (float): The minimum value for normalization.
        new_max (float): The maximum value for normalization.

    Returns:
        dict: Dictionary containing normalized values within the specified range.
    """
    # Extract all values from the data dictionary
    all_values = []
    for key, value in data.items():
        all_values.append(value)

    # Find the minimum and maximum values in the data
    min_val = min(all_values)
    max_val = max(all_values)

    # Normalize each value in the data dictionary to the specified range
    normalized = {key: new_min + (value - min_val) * (new_max - new_min) / (max_val - min_val) for key, value in data.items()}

    return normalized




def divide_dataset(df):
    """
    Divide the dataset into north, south, east, and west regions based on coordinates.

    Args:
        df (pd.DataFrame): The DataFrame with geographical data.

    Returns:
        list: List of DataFrames for north, south, east, and west regions.
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

    # Split the data into east and west regions based on longitudes
    east_data = df[df['longitude'] >= average_long]
    west_data = df[df['longitude'] < average_long]
    
    return [north_data, south_data, east_data, west_data]


def productivity_to_df(df, df_soja):
    """
    Extracts and structures productivity data from the given DataFrames.

    Args:
        df (pd.DataFrame): The primary DataFrame with geographical data.
        df_soja (pd.DataFrame): The secondary DataFrame with productivity data.

    Returns:
        pd.DataFrame: DataFrame containing structured productivity data.
    """
    # Extract unique combinations of 'name_ibge', 'year', 'latitude', and 'longitude'
    subdata_unique_name_year = df[['name_ibge', 'year', 'latitude', 'longitude']].drop_duplicates()

    # Merge DataFrames based on 'name_ibge'
    subdata_unique_name_year = pd.merge(subdata_unique_name_year, df_soja, left_on='name_ibge', right_on='name', how='left')

    # Filter out the columns from 'df_soja' that contain the numeric values
    year_columns = df_soja.columns[3:]

    # Create an empty DataFrame to store productivity values
    productivity_data = pd.DataFrame(columns=['name_ibge', 'latitude', 'longitude', 'year', 'productivity'])

    # Iterate through the merged DataFrame and check for matches
    for index, row in subdata_unique_name_year.iterrows():
        for col in year_columns:
            if row['year'] == col:
                productivity_data.loc[index] = [row['name_ibge'], row['latitude'], row['longitude'], row['year'], row[col]]

    return productivity_data

