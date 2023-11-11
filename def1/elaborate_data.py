"""
    Module for data processing and extraction from CSV files.

    Provides functions for reading CSV files, filtering rows based on productivity years,
    dropping unnecessary columns, assigning date-related columns, merging DataFrames,
    and extracting a subfile with processed data.

    Args:
        directory (str): The directory path where CSV files are located.

    Returns:
        None
"""


import os
import pandas as pd

def find_and_read_csv(directory):
    """
    Find and read CSV files in the specified directory.

    Args:
    - directory (str): The directory path where CSV files are located.

    Returns:
    - pd.DataFrame: DataFrame read from the largest CSV file.
    - pd.DataFrame: DataFrame read from the smallest CSV file.
    """
    # Find all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]
    # If no CSV files are found, inform the user and return None
    if not csv_files:
        print("No CSV files found in the directory.")
        return None, None
    # Get the size of each CSV file and sort them based on file size
    file_sizes = {file: os.path.getsize(os.path.join(directory, file)) for file in csv_files}
    sorted_files = sorted(file_sizes.items(), key=lambda x: x[1])
    # Get the largest and smallest CSV files based on size
    largest_file, smallest_file = sorted_files[-1][0], sorted_files[0][0] 
    # Read the largest and smallest CSV files into DataFrames
    df = pd.read_csv(os.path.join(directory, largest_file))
    df_soja= pd.read_csv(os.path.join(directory, smallest_file))
    return df, df_soja  # Return the DataFrames for the largest and smallest CSV files


def filter_rows(dataframe, productivity_years):
    """
    Filter rows in the DataFrame based on a specified list of productivity years.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to filter.
    - productivity_years (list): List of years considered as productivity years.

    Returns:
    - pd.DataFrame: Filtered DataFrame containing rows only with 'year' values present in productivity_years.
    """
    try:
        filtered_dataframe = dataframe[dataframe['year'].isin(productivity_years)].copy()
        return filtered_dataframe
    except KeyError as e:
        print(f"Error: {e}. 'year' column not found.")
        return pd.DataFrame()  # Return an empty DataFrame if the 'year' column is not found
    except Exception as e:
        print(f"Error: {e}. Failed to filter rows based on productivity years.")
        return dataframe  # Return the original DataFrame if an exception occurs



def drop_columns(dataframe, columns_to_keep):
    """
    Drop columns in the DataFrame that are not in the columns_to_keep list.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to process.
    - columns_to_keep (list): List of columns to keep in the DataFrame.

    Returns:
    - pd.DataFrame: DataFrame after dropping columns not in the columns_to_keep list.
    """
    try:
        # Find columns to drop that are not in the columns_to_keep list
        columns_to_drop = [col for col in dataframe.columns if col not in columns_to_keep] 
        # Drop columns not present in the columns_to_keep list
        return dataframe.drop(columns=columns_to_drop)
    except Exception as e:
        print(f"Error: {e}. Failed to drop columns.")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


def assign_date(dataframe):
    """
    Assign 'year', 'month', and 'day' columns based on the 'data' column.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: DataFrame with 'year', 'month', and 'day' columns added.
    """
    try:
        # Extract 'year', 'month', and 'day' from the 'data' column
        dataframe['year'] = dataframe['data'].astype(str).str[:4]
        dataframe['month'] = dataframe['data'].astype(str).str[4:6]
        dataframe['day'] = dataframe['data'].astype(str).str[6:8]
        return dataframe
    except KeyError as e:
        print(f"Error: {e}. 'data' column not found.")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

def add_name_ibge(df, df_soja):
    """
    Merge DataFrames to add the 'name_ibge' column.

    Args:
    - df (pd.DataFrame): The primary DataFrame.
    - df_soja (pd.DataFrame): The secondary DataFrame.

    Returns:
    - pd.DataFrame: Merged DataFrame with 'name_ibge' column added.
    """
    # Merge the primary and secondary DataFrames on the 'codigo_ibge' column, adding 'name_ibge'
    merged_df = df.merge(df_soja[['codigo_ibge', 'name']], on='codigo_ibge', how='left')
    # Rename the 'name' column to 'name_ibge' for clarity
    merged_df = merged_df.rename(columns={'name': 'name_ibge'})
    return merged_df


def assign_seasons(dataframe):
    """
    Assign 'season' column based on 'year', 'month', and 'day' columns.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: DataFrame with 'season' column added.
    """
    # Define the seasons with their corresponding start and end dates
    seasons = [
        ('Summer', ('01', '01'), ('03', '20')),
        ('Autumn', ('03', '21'), ('06', '20')),
        ('Winter', ('06', '21'), ('09', '22')),
        ('Spring', ('09', '23'), ('12', '20')),
        ('Summer', ('12', '21'), ('12', '31'))
    ]
    # Define a function to assign seasons based on month and day values
    def assign_season(row):
        month, day = row['month'], row['day']
        # Loop through the defined seasons and check for the matching period
        for season, (start_month, start_day), (end_month, end_day) in seasons:
            if (start_month <= month <= end_month) and (
                    (start_month != month or start_day <= day) and (
                        end_month != month or end_day >= day)
            ):
                return season
        # If no match found, label it as 'Unknown'
        return 'Unknown'

    # Apply the function to the DataFrame to create a new 'season' column
    dataframe['season'] = dataframe.apply(assign_season, axis=1)
    return dataframe


def extract_subfile(input_folder, output_folder):
    """
    Extract and process data, saving the result in an output folder.

    Args:
    - input_folder (str): The directory path containing input CSV files.
    - output_folder (str): The directory path to save the processed CSV file.

    Returns:
    - pd.DataFrame: The processed DataFrame.
    - pd.DataFrame: Secondary DataFrame for additional processing.
    """
    # Define the path for the output file
    output_file_path = os.path.join(output_folder, "filtered_data.csv")
    # Read the primary and secondary CSV files
    df, df_soja = find_and_read_csv(input_folder) 
    # Process the primary DataFrame by assigning 'year', 'month', and 'day' columns
    df = assign_date(df) 
    # Define columns to keep in the DataFrame
    columns_to_keep = ['year', 'month', 'day', 
                      'codigo_ibge', 'latitude', 'longitude', 
                      'TS', 'T2M', 'PS', 'GWETROOT',
                      'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN',
                      'WS2M', 'WS10M'
                    ]
    # Drop columns not present in the 'columns_to_keep' list
    df = drop_columns(df, columns_to_keep)
    # Remove extra spaces in column names in the secondary DataFrame
    df_soja.rename(columns=lambda x: x.strip(), inplace=True)
    # Define the year range for filtering the DataFrame
    productivity_years = df_soja.columns[3:]
    # Filter the primary DataFrame based on the year range
    df = filter_rows(df, productivity_years)
    # Assign 'season' column based on 'month', and 'day'
    df = assign_seasons(df)    
    # Merge DataFrames to add the 'name_ibge' column
    df = add_name_ibge(df, df_soja)
    # Save the processed DataFrame to a CSV file
    df.to_csv(output_file_path, index=False)
    # Return the processed primary DataFrame and the secondary DataFrame
    return df, df_soja
