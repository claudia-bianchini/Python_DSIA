import os
import pandas as pd

"""
    Extract and process data, saving the result in an output folder.

    Args:
    - input_folder (str): The directory path containing input CSV files.
    - output_folder (str): The directory path to save the processed CSV file.

    Returns:
    - pd.DataFrame: The processed DataFrame.
    - pd.DataFrame: Secondary DataFrame for additional processing.
    """

def find_and_read_csv(directory):
    """
    Find and read CSV files in the specified directory.

    Args:
    - directory (str): The directory path where CSV files are located.

    Returns:
    - pd.DataFrame: DataFrame read from the largest CSV file.
    - pd.DataFrame: DataFrame read from the smallest CSV file.
    """
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the directory.")
        return None, None

    file_sizes = {}
    for file in csv_files:
        file_path = os.path.join(directory, file)
        file_sizes[file] = os.path.getsize(file_path)

    sorted_files = sorted(file_sizes.items(), key=lambda x: x[1])

    largest_file, smallest_file = sorted_files[-1][0], sorted_files[0][0]

    df = pd.read_csv(os.path.join(directory, largest_file))
    df_soja = pd.read_csv(os.path.join(directory, smallest_file))

    print(f"The larger file is {largest_file} and the smaller is {smallest_file}")
    return df, df_soja

def filter_rows(dataframe, range_years):
    """
    Filter rows in the DataFrame based on a range of years.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to filter.
    - range_years (tuple): A tuple containing the start and end years for filtering.

    Returns:
    - pd.DataFrame: Filtered DataFrame based on the specified year range.
    """
    try:
        # Convert 'year' column to integers
        dataframe['year'] = pd.to_numeric(dataframe['year'], errors='coerce')

        # Filter rows based on the range of years
        #filtered_index = (dataframe['year'] >= range_years[0]) 
        # & (dataframe['year'] <= range_years[1]
        filtered_index = dataframe['year'].between(range_years[0], range_years[1])
        filtered_dataframe = dataframe.loc[filtered_index].copy()

        # Convert 'year' column back to string
        filtered_dataframe['year'] = filtered_dataframe['year'].astype(str)
        
        return filtered_dataframe
    except KeyError as e:
        print(f"Error: {e}. 'year' column not found.")
        return pd.DataFrame()  # Return an empty DataFrame if there's an issue


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
        # Drop columns that are not in the list of columns to keep
        columns_to_drop = [col for col in dataframe.columns if col not in columns_to_keep]
        dataframe = dataframe.drop(columns=columns_to_drop)
        return dataframe
    except Exception as e:
        print(f"Error: {e}. Failed to drop columns.")
        return pd.DataFrame()  # Return an empty DataFrame if there's an issue


def assign_date(dataframe):
    """
    Assign 'year', 'month', and 'day' columns based on the 'data' column.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: DataFrame with 'year', 'month', and 'day' columns added.
    """
    try:
        # Make sure the date column is in datetime format
        dataframe['year'] = dataframe['data'].astype(str).str[:4]
        dataframe['month'] = dataframe['data'].astype(str).str[4:6]
        dataframe['day'] = dataframe['data'].astype(str).str[6:8]

        return dataframe
    except KeyError as e:
        print(f"Error: {e}. 'data' column not found.")
        return pd.DataFrame()  # Return an empty DataFrame if there's an issue


def add_name_ibge(df, df_soja):
    """
    Merge DataFrames to add the 'name_ibge' column.

    Args:
    - df (pd.DataFrame): The primary DataFrame.
    - df_soja (pd.DataFrame): The secondary DataFrame.

    Returns:
    - pd.DataFrame: Merged DataFrame with 'name_ibge' column added.
    """
    # Merge the DataFrames on 'codigo_ibge' to add 'name_ibge' column
    merged_df = df.merge(df_soja[['codigo_ibge', 'name']], on='codigo_ibge', how='left')
    # Rename the 'name' column to 'name_ibge'
    merged_df = merged_df.rename(columns={'name': 'name_ibge'})
    return merged_df



# Function to assign a season
def assign_seasons(dataframe):
    """
    Assign 'season' column based on 'year', 'month', and 'day' columns.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: DataFrame with 'season' column added.
    """
    # dataframe must have column 'year', 'month', 'day'
    # Define your season criteria, including the start and end dates for each season
    seasons = [
        ('Summer', ('01', '01'), ('03', '20')),
        ('Autumn', ('03','21'), ('06','20')),
        ('Winter', ('06', '21'), ('09','22')),
        ('Spring', ('09', '23'), ('12', '20')),
        ('Summer', ('12', '21'),('12','31'))

    ]

    # Create a function to assign seasons based on dates
    def assign_season(row):
        month, day = row['month'], row['day']
        for season, (start_month, start_day), (end_month, end_day) in seasons:
            if (
                start_month <= month <= end_month
                and (start_month != month or start_day <= day)
                and (end_month != month or end_day >= day)
            ):
              return season
        return 'Unknown'

    # Apply the function to the 'Date' column to create a new 'Season' column
    dataframe['season'] = dataframe.apply(assign_season, axis = 1)

    return dataframe


# Adjust dataset by inserting columns that are useful and dropping coluns theìat we don't use    
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
    # Define the output file path within the output folder
    output_file_path = os.path.join(output_folder, "filtered_data.csv")

    df, df_soja = find_and_read_csv(input_folder)
    
    # Define a dedicated column for: year, month, day
    df = assign_date(df)
    # Drop all the column that are useless
    # Specify the columns you want to keep
    columns_to_keep = ['year', 'month', 'day', 
                        'codigo_ibge', 'latitude', 'longitude', 
                        'TS', 'PS', 'GWETROOT']
    df = drop_columns(df, columns_to_keep)
    # Create a filtered dataset for agroclimatology.csv 
    # because produtividade_soja.csv has years only from 2004, 2017
    range_years = (2004, 2017)
    df = filter_rows(df, range_years)
    
    # Define the season
    df = assign_seasons(df)

    # Rename productivade_soja.csv's columns:
    df_soja.rename(columns=lambda x: x.strip(), inplace=True)
    
    # Add column 'name_ibge' from productividade
    df = add_name_ibge(df, df_soja)

    # Save the adjusted DataFrame to a CSV file
    output_file_path = os.path.join(output_folder, "filtered_data.csv")
    df.to_csv(output_file_path, index=False)
    return df, df_soja


# def test_functions():
#     # Test dataset for validation
#     test_data = {
#         'data': ['20210501', '20191215', '20220130'],
#         'year': [2021, 2019, 2022],
#         'TS': [25, 30, 27],
#         'PS': [1000, 980, 1020]
#     }
#     df = pd.DataFrame(test_data)

#     # Test filter_rows function
#     filtered_data = filter_rows(df, (2019, 2021))
#     print("Filtered Data:")
#     print(filtered_data)

#     # Test drop_columns function
#     columns_to_keep = ['year', 'data', 'TS']
#     modified_data = drop_columns(df, columns_to_keep)
#     print("Modified Data:")
#     print(modified_data)

#     # Test assign_date function
#     dated_data = assign_date(df)
#     print("Dated Data:")
#     print(dated_data)


    # Add a call to the test function for validating the functions
    # test_functions()

