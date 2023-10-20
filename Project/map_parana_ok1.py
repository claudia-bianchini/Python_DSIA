import pandas as pd
import folium




# Import data
fullpath = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(fullpath)

# Define the path to the output folder
output_folder = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output'
map_path = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\map.html'

# Specify the specific date you want to find
specific_date = 20160101

# Filter the DataFrame to select rows with the specific date
specific_df = df[df["data"] == specific_date]
print(specific_df)

# Create a set to store unique [latitude, longitude] pairs
unique_coordinates = set()

# Iterate through the rows and add unique pairs to the set
for _, row in specific_df.iterrows():
    coordinate_pair = (row["latitude"], row["longitude"])
    unique_coordinates.add(coordinate_pair)

# Create a folium map centered around the first unique pair
m = folium.Map(location = unique_coordinates.pop(), zoom_start=10)

# Add markers for the unique pairs on the map
for pair in unique_coordinates:
    folium.Marker(
        location=pair,
        popup=f'Latitude: {pair[0]}, Longitude: {pair[1]}'
    ).add_to(m)

# Save the map to an HTML file

m.save(map_path)
