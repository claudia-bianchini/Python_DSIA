import pandas as pd
import folium


# Import data
path_filtered_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(path_filtered_data)

path_soja_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\input\produtividade_soja.csv' #here there are the name of the municipal
df_soja = pd.read_csv(path_soja_data)

# Define the path to the output folder
output_folder = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output'
map_path = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\map.html'

# Specify the specific date you want to find
specific_date = 20160101

# Filter the DataFrame to select rows with the specific date
specific_df = df[df["data"] == specific_date]
#print(specific_df)


#print(specific_df)
# Create a set to store unique [latitude, longitude] pairs
#unique_coordinates = set()

# Iterate through the rows and add unique pairs to the set
# for _, row in specific_df.iterrows():
#     coordinate_pair = (row['name_ibge'], row["latitude"], row["longitude"])
#     unique_coordinates.add(coordinate_pair)
# unique_coordinates = specific_df[specific_df['latitude'],specific_df['longitude']]
# Assuming your DataFrame is named 'df'
df = df.drop_duplicates(subset=['latitude', 'longitude'])
#Add to the Filtered Dataframe another column with the name of the minicipal

for index, row in specific_df.iterrows():
    try:
        for soja_index, soja_row in df_soja.iterrows():
            if row['codigo_ibge'] == soja_row['codigo_ibge']:
                specific_df.at[index, 'name_ibge'] = soja_row['name']
    except: pass

print(specific_df)
#Extract the coordinates to simpler manage the map
# unique_coordinates = specific_df[['latitude', 'longitude']]
# print(unique_coordinates)

# Create a folium map centered around the first unique pair
m = folium.Map(location=[specific_df.iloc[0]['latitude'], specific_df.iloc[0]['longitude']], zoom_start=10)
# m = folium.Map(location = unique_coordinates.iloc[0], zoom_start=10)

# Add markers for the unique pairs on the map
# for pair in unique_coordinates:
#     folium.Marker(
#         location = pair,
#         popup = f'{specific_df.iloc['name_ibge']}, Latitude: {pair['latitude']} Longitude: {pair['longitude']}'
    
#     ).add_to(m)
for index, row in specific_df.iterrows():
    folium.Marker(
        location=(row['latitude'], row['longitude']),
        popup=f"{row['name_ibge']}, Latitude: {row['latitude']} Longitude: {row['longitude']}"
    ).add_to(m)


# Save the map to an HTML file
m.save(map_path)
