import os.path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#def take_data:
# Import data
fullpath = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(fullpath)

#return df


#def find_coord
# Initialize lists to store latitude and longitude values
latitudes = set()
longitudes = set()
coords = set()

#Find the vector of latitude and longitude
for index, row in df.iterrows():
        coords.add([float(row["latitude"]), float(row["longitude"])])

# print(len(latitudes))
# print(len(longitudes))
# #return coord([latitudes, longitudes])
# coords = [[latitudes, longitudes]]
print(coords)
        
#We want to define the limit of the geometry;
most_north = max(coords[0])
most_south = min(coords[0])

most_est = min(coords[1])
most_south = max(coords[1])

average_lat = coords[0].mean
average_long = coords[1].mean
# center_lat = takeClosest(coord[0], average_lat)
# center_log = takeClosest(coord[1], average_long)

#We devide the dataset in place that are in the north and the one that are int he south:
north_data = []
south_data = []
for row in df.iterrows():
    if row['latitude'] <= average_lat:
        north_data.append(row)
    else:
        south_data.append(row)

#We group north_data by year:
north_data['year'] = north_data['data'].astype(str).str[:4]
north_data = north_data.groupby('year')
#We want to plot the mean annual temperature depending on the position:
north_mean_temp_TS = north_data.groupby('year')['TS'].mean()
north_mean_temp_T2MWET = north_data.groupby('year')['T2MWET'].mean()
north_mean_temp_T2M = north_data.groupby('year')['T2M'].mean()
north_mean_humidity_QV2M = north_data.groupby('year')['QV2M'].mean()
north_mean_pressure = north_data.groupby('year')['PS'].mean()

#We do the same with south_data:
south_data['year'] = south_data['data'].astype(str).str[:4]
south_data = south_data.groupby('year')
#We want to plot the mean annual temperature depending on the position:
south_mean_temp_TS = south_data.groupby('year')['TS'].mean()
south_mean_temp_T2MWET = south_data.groupby('year')['T2MWET'].mean()
south_mean_temp_T2M = south_data.groupby('year')['T2M'].mean()
south_mean_humidity_QV2M = south_data.groupby('year')['QV2M'].mean()
south_mean_pressure = south_data.groupby('year')['PS'].mean()

#Plot north_data in an histogram

# Create a figure and subplots
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Create histograms on each subplot
axes[0].hist(north_mean_temp_TS, bins=20, color='blue', alpha=0.7)
axes[0].set_title('TS')

axes[1].hist(south_mean_temp_TS, bins=20, color='green', alpha=0.7)
axes[1].set_title('TS')



# Set common labels for all subplots
for ax in axes:
    ax.set_xlabel('TS')
    ax.set_ylabel('Frequency')

# Add a title to the entire figure
fig.suptitle('TS variation between north and south')

# Display the figure
plt.show()