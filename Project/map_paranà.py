import csv
import folium
import pandas as pd


#Read the CSV file into a Dataframe
df = pd.read_csv('filtered_data.csv')

#We have different positional measurment per each day (equal per every day)
#We choose a specific day and we filter the dataframe to have a new one that has only 
#data for that day
specific_day = 20080101 
#print(type(df['data']))

df_specific_day = df[df['data'] == specific_day]
print(df_specific_day)


# Create a set to store unique [latitude, longitude] pairs
unique_coordinates = set()

# Iterate through the rows and add unique pairs to the set
for _, row in df_specific_day.iterrows():
    coordinate_pair = (row["latitude"], row["longitude"])
    unique_coordinates.add(coordinate_pair)

            
map = folium.Map(location = [unique_coordinates.pop()], zoom_start = 10)

#To add markers we have to iterate through rows

for pair in unique_coordinates.iterrows():
    folium.Marker(
        location = pair,
        popup = f'Latitude: {pair[0]}, Longitude: {pair[1]}'
    ).add_to(map)

#Save the map as HTML file
map.save('map.html')

