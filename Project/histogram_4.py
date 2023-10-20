import os.path
import pandas as pd
import matplotlib.pyplot as plt


#Function to assign a season
# def assign_seasons(dataframe):
#     # Make sure the date column is in datetime format
#     dataframe['data'] = pd.to_datetime(dataframe['data'])
    
#     # Define your season criteria, for example, assuming the start and end dates for each season
#     seasons = [
#         ('Winter', pd.date_range(start='0101', end='0320')),
#         ('Spring', pd.date_range(start='0321', end='0620')),
#         ('Summer', pd.date_range(start='0621', end='0922')),
#         ('Autumn', pd.date_range(start='0923', end='1220')),
#         ('Winter', pd.date_range(start='1221', end='1231'))
#     ]
    
#     # Create a function to assign seasons based on dates
#     def assign_season(date):
#         for season, date_range in seasons:
#             if date[5:8] in date_range:
#                 return season
#         return 'Unknown'
    
#     # Apply the function to the 'Date' column to create a new 'Season' column
#     dataframe['season'] = dataframe['data'].apply(assign_season)
    
#     return dataframe

# Function to assign a season
def assign_seasons(dataframe):
    # Make sure the date column is in datetime format
    dataframe['data'] = pd.to_datetime(dataframe['data'])
    
    # Define your season criteria, including the start and end dates for each season
    seasons = [
        ('Winter', (pd.Timestamp('0101'), pd.Timestamp('0320'))),
        ('Spring', (pd.Timestamp('0321'), pd.Timestamp('0620'))),
        ('Summer', (pd.Timestamp('0621'), pd.Timestamp('0922'))),
        ('Autumn', (pd.Timestamp('0923'), pd.Timestamp('1220'))),
        ('Winter', (pd.Timestamp('1221'), pd.Timestamp('1231')))
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


# Import data
fullpath = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(fullpath)

df = assign_seasons(df)

# Extract latitude and longitude
latitudes = df['latitude']
longitudes = df['longitude']

# Find the northernmost, southernmost, easternmost, and westernmost coordinates
most_north = latitudes.max()
most_south = latitudes.min()
most_east = longitudes.min()
most_west = longitudes.max()

# Calculate average latitude and longitude
average_lat = (most_north+most_south)/2
average_long = (most_east+most_west)/2

print(f'Lat max: ', most_north)
print(f'Lat min: ', most_south)
print(f'Lat average: ', average_lat)

# Split the data into north and south regions based on latitude
north_data = df[df['latitude'] >= average_lat]
south_data = df[df['latitude'] < average_lat]

print(f'Number of commun in the north: ', len(north_data))
print(f'Number of commun in the south: ', len(south_data))


# Group the data by year
north_data['year'] = north_data['data'].astype(str).str[:3]
south_data['year'] = south_data['data'].astype(str).str[:3]
#print(f'North Data: ', north_data)

north_data_year = north_data.groupby('year')
south_data_year = south_data.groupby('year')

#print(f'North Data after groupby year: ', north_data)


# Calculate the mean for the columns you are interested in
north_mean_temp_TS = north_data_year['TS'].mean()
south_mean_temp_TS = south_data_year['TS'].mean()

print(f'Mean in the north: ', len(north_mean_temp_TS))
print(f'Mean in the south: ', len(south_mean_temp_TS))


# Create histograms to visualize the TS variation between north and south
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

axes[0].hist(north_mean_temp_TS, bins=20, color='blue', edgecolor='black', alpha=0.7)
axes[0].set_title('North Region - TS')

axes[1].hist(south_mean_temp_TS, bins=20, color='green', edgecolor='black', alpha=0.7)
axes[1].set_title('South Region - TS')

for ax in axes:
    ax.set_xlabel('TS')
    ax.set_ylabel('Frequency')

fig.suptitle('Year mean TS Variation in North vS South Regions')

plt.show()



#Now plot mean Temperature of the season:
# Group the data by season

north_data_season = north_data_year.get_group('season')
south_data_season = south_data_year.get_group('season')

north_TS_winter = north_data_year.loc[north_data_year['season'] == 'Winter', 'TS']
south_TS_winter = southth_data_year.loc[south_data_year['season'] == 'Winter', 'TS']

fig, axes = plt.subplots(1, 2, figsize=(10, 5))

axes[0].hist(north_TS_winter, bins=20, color='blue', edgecolor='black', alpha=0.7)
axes[0].set_title('North Region - TS')

axes[1].hist(south_TS_winter, bins=20, color='green', edgecolor='black', alpha=0.7)
axes[1].set_title('South Region - TS')

for ax in axes:
    ax.set_xlabel('TS')
    ax.set_ylabel('Frequency')

fig.suptitle('Year mean TS Variation in North vS South Regions')

plt.show()
