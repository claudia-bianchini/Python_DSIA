import os.path
import pandas as pd
import matplotlib.pyplot as plt

# Function to assign a season
def assign_seasons(dataframe):
    # Make sure the date column is in datetime format
    dataframe['data'] = pd.to_datetime(dataframe['data'], '%y%m%d')

    # Define your season criteria, including the start and end dates for each season
    seasons = [
        ('Winter', (pd.Timestamp('01-01'), pd.Timestamp('03-20'))),
        ('Spring', (pd.Timestamp('03-21'), pd.Timestamp('06-20'))),
        ('Summer', (pd.Timestamp('06-21'), pd.Timestamp('09-22'))),
        ('Autumn', (pd.Timestamp('09-23'), pd.Timestamp('12-20'))),
        ('Winter', (pd.Timestamp('12-21'), pd.Timestamp('12-31')))
    ]

    # Create a function to assign seasons based on dates
    def assign_season(date):
        for season, (start_date, end_date) in seasons:
            if start_date <= date <= end_date:
                return season
        return 'Unknown'

    # Apply the function to the 'Date' column to create a new 'Season' column
    dataframe['season'] = dataframe['data'].apply(assign_season)

    return dataframe

def assign_year(dataframe):
    # Make sure the date column is in datetime format
    dataframe['data'] = pd.to_datetime(dataframe['data'])
    
    # Extract the year from the 'date' column and create a new column 'year'
    dataframe['year'] = dataframe['data'].dt.year
    
    return dataframe

# Import data
fullpath = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(fullpath)

# Assign seasons
df = assign_seasons(df)

# Assign year to each row
df = assign_year(df)

print(df)
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

# Split the data into north and south regions based on latitude
north_data = df[df['latitude'] >= average_lat]
south_data = df[df['latitude'] < average_lat]

print(f'Number of common in the north: ', len(north_data))
print(f'Number of common in the south: ', len(south_data))

# Group the data by year
north_data_year = north_data.groupby('year')
south_data_year = south_data.groupby('year')

# Create histograms to visualize the TS variation between north and south
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

north_TS_winter = north_data_year.get_group('2016')['TS']  # Change the year to the one you're interested in
south_TS_winter = south_data_year.get_group('2016')['TS']  # Change the year to the one you're interested in

axes[0].hist(north_TS_winter, bins=20, color='blue', edgecolor='black', alpha=0.7)
axes[0].set_title('North Region - TS')

axes[1].hist(south_TS_winter, bins=20, color='green', edgecolor='black', alpha=0.7)
axes[1].set_title('South Region - TS')

for ax in axes:
    ax.set_xlabel('TS')
    ax.set_ylabel('Frequency')

fig.suptitle('Year TS Variation in North vs South Regions WINTER')

plt.show()
