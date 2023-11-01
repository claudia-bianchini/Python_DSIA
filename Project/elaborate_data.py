import csv
import os
import pandas as pd



def filter_rows(dataframe, range_years):
    # Convert 'year' column to integers
    dataframe['year'] = dataframe['year'].astype(int)
    
    # Filter rows based on the range of years
    filtered_index = (dataframe['year'] >= range_years[0]) & (dataframe['year'] <= range_years[1])
    filtered_dataframe = dataframe.loc[filtered_index].copy()
    
    # Convert 'year' column back to string
    filtered_dataframe['year'] = filtered_dataframe['year'].astype(str)
    
    return filtered_dataframe




def drop_columns(dataframe, columns_to_keep):
    # Drop columns that are not in the list of columns to keep
    columns_to_drop = [col for col in dataframe.columns if col not in columns_to_keep]
    dataframe = dataframe.drop(columns=columns_to_drop)
    return dataframe


def assign_date(dataframe):
    # Make sure the date column is in datetime format
    dataframe['year'] = dataframe['data'].astype(str).str[:4]
    dataframe['month'] = dataframe['data'].astype(str).str[4:6]
    dataframe['day'] = dataframe['data'].astype(str).str[6:8]

    return dataframe


def add_name_ibge(df, df_soja):
    #Add to the Filtered Dataframe another column with the name of the minicipal
    # df['name_ibge'] = ''    #Initialize the 'name_ibge' column
    df.insert(loc = 2, column = 'name_ibge', value = '')

    for df_index, df_row in df.iterrows():
        for soja_index, soja_row in df_soja.iterrows():
            if df_row['codigo_ibge'] == soja_row['codigo_ibge']:
                df.at[df_index, 'name_ibge'] = soja_row['name']
                
    return df


# Function to assign a season
def assign_seasons(dataframe):
    # dataframe must have column 'year', 'month', 'day'
    # Define your season criteria, including the start and end dates for each season
    seasons = [
        ('Winter', ('01', '01'), ('03', '20')),
        ('Spring', ('03','21'), ('06','20')),
        ('Summer', ('06', '21'), ('09','22')),
        ('Autumn', ('09', '23'), ('12', '20')),
        ('Winter', ('12', '21'),('12','31'))

    ]

    # Create a function to assign seasons based on dates
    def assign_season(row):
        year, month, day = row['year'], row['month'], row['day']
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
def adjust_data(df, df_soja):
    
    # Define a dedicated column for: year, month, day
    df = assign_date(df)
    
    # Drop all the column that are useless
    # Specify the columns you want to keep
    columns_to_keep = ['year', 'month', 'day', 'codigo_ibge', 'latitude', 'longitude', 'TS', 'PS']
    df = drop_columns(df, columns_to_keep)
    # Create a filtered dataset for agroclimatology.csv because produtividade_soja.csv has years only from 2004, 2017
    range_years = (2004, 2005)
    df = filter_rows(df, range_years)
    # Define the season
    df = assign_seasons(df)

    # Rename productivade_soja.csv's columns:
    df_soja.rename(columns=lambda x: x.strip(), inplace=True)

    # Add column 'name_ibge' from productividade
    df = add_name_ibge(df, df_soja)

    return df


# def extract_subfile():
def main():
    # Define the path to the input CSV file
    input_file_path = './input/agroclimatology.csv'

    # Define the path to the output folder
    output_folder = './output'

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Define the output file path within the output folder
    output_file_path = os.path.join(output_folder, "filtered_data.csv")

    # # Create a filtered dataset fro agroclimatology.csv because produtividade_soja.csv has years only from 2004, 2017
    # range_years = (2004, 2006)
    # # filter_data(input_file_path, output_file_path, range_years)
    
    # # Import data
    # path_filtered_data = './output/filtered_data.csv'
    df = pd.read_csv(input_file_path)

    path_soja_data = './input/produtividade_soja.csv' #here there are the name of the municipal
    df_soja = pd.read_csv(path_soja_data)

    # Adjust data
    adjusted_df = adjust_data(df, df_soja)

    # Save the adjusted DataFrame to a CSV file
    output_file_path_adjusted = os.path.join(output_folder, "filtered_data.csv")
    adjusted_df.to_csv(output_file_path, index=False)

if __name__ == "__main__":
    main()    
