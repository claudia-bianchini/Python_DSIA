import os.path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Import data
fullpath = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(fullpath)

# Define places for histograms
places = {
    'est': [-25.5427, -54.5827],
    'west': [-25.9311, -49.195],
    'center_long': [-24.438, -51.9454],
    'north': [-22.5523, -52.0503],
    'south': [-26.4839, -51.9888],
    'center_lat': [-24.438, -51.9454],
}


# Iterate through places and create histograms
for i, (place, coordinates) in enumerate(places.items()):
    latitude = coordinates[0]
    longitude = coordinates[1]
    
    # Filter rows for the specific location
    #new_df = df[(df['latitude'] == latitude) & (df['longitude'] == longitude)]
    new_df = df
    # Group the DataFrame by the first four characters of the "data" column and calculate the mean for the "TS" column
    new_df['year'] = new_df['data'].astype(str).str[:4]
    mean_temp_TS = new_df.groupby('year')['TS'].mean()
    mean_temp_T2MWET = new_df.groupby('year')['T2MWET'].mean()
    mean_temp_T2M = new_df.groupby('year')['T2M'].mean()
    mean_humidity_QV2M = new_df.groupby('year')['QV2M'].mean()
    mean_pressure = new_df.groupby('year')['PS'].mean()
    # Print the result
    print(mean_temp_TS)

# Create a histogram
# plt.hist(mean_temp_TS, bins=5, color='skyblue', edgecolor='black')

# # Customize the plot
# plt.xlabel('Temperature')
# plt.ylabel('Occurrency')
# plt.title('Mean temperature along the years')

# # Display the histogram
# plt.show()




# # Adjust layout and display
# plt.tight_layout(rect=[0, 0.03, 1, 0.95])
# plt.show()


# Create a figure and subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Create histograms on each subplot
axes[0].hist(mean_temp_TS, bins=20, color='blue', alpha=0.7)
axes[0].set_title('Histogram 1')

axes[1].hist(mean_temp_T2MWET, bins=20, color='green', alpha=0.7)
axes[1].set_title('Histogram 2')

axes[2].hist(mean_temp_T2M, bins=20, color='red', alpha=0.7)
axes[2].set_title('Histogram 3')

# Set common labels for all subplots
for ax in axes:
    ax.set_xlabel('X-axis Label')
    ax.set_ylabel('Frequency')

# Add a title to the entire figure
fig.suptitle('Subplots with Histograms')

# Display the figure
plt.show()