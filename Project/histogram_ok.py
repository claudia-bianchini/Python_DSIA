import os.path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mcols

# Function to assign a season
def assign_seasons(dataframe):
    # Make sure the date column is in datetime format
    dataframe['year'] = dataframe['data'].astype(str).str[:4]
    dataframe['month'] = dataframe['data'].astype(str).str[4:6]
    dataframe['day'] = dataframe['data'].astype(str).str[6:8]
    #print(dataframe)
    # Define your season criteria, including the start and end dates for each season
    seasons = [
        ('Winter', ('01', '01'), ('03', '20')),
        ('Spring', ('03','21'), ('06','20')),
        ('Summer', ('06', '21'), ('09','22')),
        ('Autumn', ('09', '23'), ('12', '20')),
        ('Winter', ('12', '21'),('12','31'))

    ]

    # Create a function to assign seasons based on dates
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

def group_year(dataframe):
    # Group the DataFrame by the 'year' column
    grouped = df.groupby('year')
    
    # Return a dictionary of DataFrames, where each key is a year and the corresponding value is the DataFrame for that year
    #yearly_data = {year: group for year, group in grouped}
    
    return grouped #yearly_data

# Import data
fullpath = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(fullpath)

# Assign seasons
df = assign_seasons(df)

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

print(f'Lat max: ', most_north)
print(f'Lat min: ', most_south)
print(f'Lat average: ', average_lat)
print(f'Long average: ', average_long)

# Split the data into north and south regions based on latitude
north_data = df[df['latitude'] <= average_lat]
south_data = df[df['latitude'] > average_lat]

print(f'Number of data in the north: ', len(north_data))
print(f'Number of data in the south: ', len(south_data))

# Split the data into north and south regions based on longitudes
east_data = df[df['longitude'] >= average_long]
west_data = df[df['longitude'] < average_long]

print(f'Number of common in the east: ', len(east_data))
print(f'Number of common in the west: ', len(west_data))

#Groupby Each dataset for year
north_data_year = north_data.groupby('year')
south_data_year = south_data.groupby('year')
east_data_year = east_data.groupby('year')
west_data_year = west_data.groupby('year')

# Calculate the mean for the 'TS' column
north_mean_temp_TS = north_data_year['TS'].mean()
south_mean_temp_TS = south_data_year['TS'].mean()

print(f'Mean in the north: ', len(north_mean_temp_TS))
print(f'Mean in the south: ', len(south_mean_temp_TS))

# Extract the data we want to plot

north_TS_winter = north_data_year.get_group('2015')[north_data_year.get_group('2015')['season'] == 'Winter']['TS']
south_TS_winter = south_data_year.get_group('2015')[south_data_year.get_group('2015')['season'] == 'Winter']['TS']

east_TS_winter = east_data_year.get_group('2015')[east_data_year.get_group('2015')['season'] == 'Winter']['TS']
west_TS_winter = west_data_year.get_group('2015')[west_data_year.get_group('2015')['season'] == 'Winter']['TS']

'''
# Create histograms to visualize the TS variation between north and south
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

axes[0].hist(north_mean_temp_TS, bins=20, color='blue', edgecolor='black', alpha=0.7)
axes[0].set_title('North Region - TS')

axes[1].hist(south_mean_temp_TS, bins=20, color='green', edgecolor='black', alpha=0.7)
axes[1].set_title('South Region - TS')

for ax in axes:
    ax.set_xlabel('TS')
    ax.set_ylabel('Frequency')

fig.suptitle('Year Mean TS Variation in North vs South Regions')

plt.show()


# Create histograms to visualize the TS variation between north and south
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

#north_TS_winter = north_data_year.get_group('2015')[north_data_year.get_group('2015')['season'] == 'Winter']['TS']
#south_TS_winter = south_data_year.get_group('2015')[south_data_year.get_group('2015')['season'] == 'Winter']['TS']
#north_TS_winter = north_data_year[north_data_year['season' == 'winter']].get_group('2016')['TS']  # Change the year to the one you're interested in
#south_TS_winter = south_data_year.get_group('2016')['TS']  # Change the year to the one you're interested in

axes[0].hist(north_TS_winter, bins=20, color='blue', edgecolor='black', alpha=0.7)
axes[0].set_title('North Region - TS')

axes[1].hist(south_TS_winter, bins=20, color='green', edgecolor='black', alpha=0.7)
axes[1].set_title('South Region - TS')

for ax in axes:
    ax.set_xlabel('TS')
    ax.set_ylabel('Events')

fig.suptitle('Year TS Variation in North vs South Regions WINTER')

plt.show()

# Create histograms to visualize the TS variation between esat and west
fig, axes = plt.subplots(1, 2, figsize=(10, 5))



#east_TS_winter = east_data_year.get_group('2015')[east_data_year.get_group('2015')['season'] == 'Winter']['TS']
#west_TS_winter = west_data_year.get_group('2015')[west_data_year.get_group('2015')['season'] == 'Winter']['TS']

axes[0].hist(east_TS_winter, bins=100, color='blue', edgecolor='black', alpha=0.7)
axes[0].set_title('East Region - TS')

axes[1].hist(west_TS_winter, bins=100, color='green', edgecolor='black', alpha=0.7)
axes[1].set_title('West Region - TS')

for ax in axes:
    ax.set_xlabel('TS')
    ax.set_ylabel('Events')

fig.suptitle('Year TS Variation in East vs South Regions WINTER')

plt.show()
'''

#Try to plot the histogram in one plot 
common_plot_params = {
    'density': True,
    #'alpha': 0.6,
    #'range': (0, 1e4),
    'bins': 100,
    'histtype': 'stepfilled'
    
}

fig, ax = plt.subplots()

ax.hist(north_TS_winter, label = 'North', color=mcols.to_rgba('tab:blue', 0.2), edgecolor='tab:blue', **common_plot_params)
ax.hist(south_TS_winter, label = 'South',color=mcols.to_rgba('tab:orange', 0.2), edgecolor='tab:orange', **common_plot_params)

#for ax in axes:
ax.set_xlabel('TS')
ax.set_ylabel('Events')
    
fig.suptitle('Year TS Variation in North vs South Regions WINTER')
ax.legend(frameon=False, loc='upper left')

plt.show()


fig, ax = plt.subplots()

ax.hist(east_TS_winter, label = 'East', color=mcols.to_rgba('tab:purple', 0.2), edgecolor='tab:purple', **common_plot_params)
ax.hist(west_TS_winter, label = 'West', color=mcols.to_rgba('tab:olive', 0.2), edgecolor='tab:olive', **common_plot_params)

#for ax in axes:
ax.set_xlabel('TS')
ax.set_ylabel('Events')

fig.suptitle('Year TS Variation in East vs West Regions WINTER')
ax.legend(frameon=False, loc='upper left')

plt.show()

