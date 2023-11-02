import os.path
import pandas as pd
import matplotlib.pyplot as plt
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

def plotting(north_TS_winter, south_TS_winter, east_TS_winter, west_TS_winter):
    # Common plot parameters
    common_plot_params = {
        'density': True,
        'bins': 100,
        'histtype': 'stepfilled'
    }

    # Create subplots for both histograms
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot the North vs South histogram
    axes[0].hist(north_TS_winter, label='North', color=mcols.to_rgba('tab:blue', 0.2), edgecolor='tab:blue', **common_plot_params)
    axes[0].hist(south_TS_winter, label='South', color=mcols.to_rgba('tab:orange', 0.2), edgecolor='tab:orange', **common_plot_params)
    axes[0].set_xlabel('TS')
    axes[0].set_ylabel('Events')
    axes[0].set_title('Year TS Variation in North vs South Regions WINTER')
    axes[0].legend(frameon=False, loc='upper left')

    # Plot the East vs West histogram
    axes[1].hist(east_TS_winter, label='East', color=mcols.to_rgba('tab:purple', 0.2), edgecolor='tab:purple', **common_plot_params)
    axes[1].hist(west_TS_winter, label='West', color=mcols.to_rgba('tab:olive', 0.2), edgecolor='tab:olive', **common_plot_params)
    axes[1].set_xlabel('TS')
    axes[1].set_ylabel('Events')
    axes[1].set_title('Year TS Variation in East vs West Regions WINTER')
    axes[1].legend(frameon=False, loc='upper left')

    # Adjust layout
    plt.tight_layout()



def histo():
    # Import data
    fullpath = './output/filtered_data.csv'
    df = pd.read_csv(fullpath)

    df['year'] = df['year'].astype(str)
    
    # Devide dataset depending on the position of the measurment
    [north_data, south_data, east_data, west_data] = devide_dataset(df)

    
    #Groupby Each dataset for year
    north_data_year = north_data.groupby('year')
    south_data_year = south_data.groupby('year')
    east_data_year = east_data.groupby('year')
    west_data_year = west_data.groupby('year')

    # Extract the data we want to plot

    north_TS_winter = north_data_year.get_group('2004')[north_data_year.get_group('2004')['season'] == 'Winter']['TS']
    south_TS_winter = south_data_year.get_group('2004')[south_data_year.get_group('2004')['season'] == 'Winter']['TS']

    east_TS_winter = east_data_year.get_group('2004')[east_data_year.get_group('2015')['season'] == 'Winter']['TS']
    west_TS_winter = west_data_year.get_group('2004')[west_data_year.get_group('2015')['season'] == 'Winter']['TS']

 
    plotting(north_TS_winter, south_TS_winter, east_TS_winter, west_TS_winter)

    # Show the combined plot
    plt.show()

histo()
