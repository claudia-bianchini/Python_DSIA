import pandas as pd
import folium
from matplotlib import colors as mcols

def assign_date(dataframe):
# Make sure the date column is in datetime format
    dataframe['year'] = dataframe['data'].astype(str).str[:4]
    dataframe['month'] = dataframe['data'].astype(str).str[4:6]
    dataframe['day'] = dataframe['data'].astype(str).str[6:8]

    return dataframe


# Import data
path_filtered_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(path_filtered_data)

path_soja_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\input\produtividade_soja.csv' #here there are the name of the municipal
df_soja = pd.read_csv(path_soja_data)

# Define the path to the output folder
output_folder = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output'
map_path = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\map.html'

df = assign_date(df)

# Specify the specific date you want to find
#specific_date = 20160101
year = '2016'

# Filter the DataFrame to select rows with the specific date
# specific_df = df[df["data"] == specific_date]
specific_df = df[df["year"] == year]
print(specific_df)
#print(type(specific_df['latitude'].iloc[10]))
print(type(df_soja['codigo_ibge'].iloc[2])) 
# Unique coordinates
df = df.drop_duplicates(subset=[df['latitude'], df['longitude']])
print(specific_df)
#Add to the Filtered Dataframe another column with the name of the minicipal
specific_df = specific_df.merge(df_soja[['codigo_ibge', 'name']], on='codigo_ibge', how='left')
# for index, row in specific_df.iterrows():
#     try:
#         for soja_index, soja_row in df_soja.iterrows():
#             if row['codigo_ibge'] == soja_row['codigo_ibge']:
#                 specific_df.at[index, 'name_ibge'] = soja_row['name']
#                 specific_df.at[index, year] = soja_row[year]
#     except: pass

# Ensure the 'name_ibge' column is of data type str
specific_df['name_ibge'] = specific_df['name_ibge'].str.strip()
#print(specific_df)

# Add the soja production to the main dataset (if present)


# Create a folium map centered around the first unique pair
m = folium.Map(location=[specific_df.iloc[0]['latitude'], specific_df.iloc[0]['longitude']], zoom_start=10)

# Draw circles for the unique pairs on the map
for index, row in specific_df.iterrows():
    folium.Circle(
        location=(row['latitude'], row['longitude']),
        popup=f"{row['name_ibge']}, Latitude: {row['latitude']} Longitude: {row['longitude']}",
        radius={row[year]},  # Radius in meters
        color='blue',
        fill=True,
        fill_color=mcols.to_rgba('tab:blue', 0.2)
        
    ).add_to(m)

# Save the map to an HTML file
m.save(map_path)