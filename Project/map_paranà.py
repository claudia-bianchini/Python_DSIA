import pandas as pd
import folium
from matplotlib import colors as mcols

def assign_date(dataframe):
# Make sure the date column is in datetime format
    dataframe['year'] = dataframe['data'].astype(str).str[:4]
    dataframe['month'] = dataframe['data'].astype(str).str[4:6]
    dataframe['day'] = dataframe['data'].astype(str).str[6:8]

    return dataframe

import pandas as pd

def rename_col(dataframe, rename_dictionary):
    """
    Rinomina le colonne di un DataFrame utilizzando un dizionario di mappatura.

    Args:
        dataframe (pd.DataFrame): Il DataFrame da rinominare.
        dizionario_rinomina (dict): Un dizionario che mappa i nomi delle colonne originali ai nuovi nomi.

    Returns:
        pd.DataFrame: Il DataFrame con le colonne rinominate.
    """
    return dataframe.rename(columns=rename_dictionary)



# Import data
path_filtered_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(path_filtered_data)

path_soja_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\input\produtividade_soja.csv' #here there are the name of the municipal
df_soja = pd.read_csv(path_soja_data)

#We need ro rename the column:
colums_rename = {'nivel ': 'nivel', 'codigo_ibge ': 'codigo_ibge', 'name                        ': 'name',
                     '2004   ' : '2004', '2005   ' : '2005', '2006   ' : '2006', '2007   ' : '2007', '2008   ': '2008', 
                     '2009   ' : '2009', '2010   ' : '2010', '2011   ' : '2011', '2012   ' : '2012', '2013   ' : '2013', 
                     '2014   ' : '2014', '2015   ' : '2015', '2016   ' : '2016', '2017' : '2017'}
df_soja = rename_col(df_soja, colums_rename)

print(df_soja.columns)


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
#print(specific_df)
# Unique coordinates
specific_df = specific_df.drop_duplicates(subset=['latitude', 'longitude'])
#print(specific_df)
#Add to the Filtered Dataframe another column with the name of the minicipal
specific_df['name_ibge'] = ''    #Initialize the 'name_ibge' column
specific_df['production'] = ''

#print(specific_df.columns)
#print(df_soja.columns)
for df_index, df_row in specific_df.iterrows():
    try:
        for soja_index, soja_row in df_soja.iterrows():
            if df_row['codigo_ibge'] == soja_row['codigo_ibge']:
                specific_df.at[df_index, 'name_ibge'] = soja_row['name']
                specific_df.at[df_index, 'production'] = soja_row['2016']
                pass
    except: pass
print(specific_df['production'].iloc[1])
print(specific_df)
# Ensure the 'name_ibge' column is of data type str
specific_df['name_ibge'] = specific_df['name_ibge'].str.strip()
#print(specific_df)

# Add the soja production to the main dataset (if present)


# Create a folium map centered around the first unique pair

if not specific_df.empty:
    m = folium.Map(location=[specific_df.iloc[1]['latitude'], specific_df.iloc[1]['longitude']], zoom_start=10)

    # Draw circles for the unique pairs on the map
    for index, row in specific_df.iterrows():
        folium.Circle(
            location=(row['latitude'], row['longitude']),
            popup=f"{row['name_ibge']}, Latitude: {row['latitude']} Longitude: {row['longitude']}",
            radius=row['production']*1.5,  # Radius in meters
            color='blue',
            fill=True,
            fill_color=mcols.to_rgba('tab:blue', 0.2)
            
        ).add_to(m)

    # Save the map to an HTML file
    m.save(map_path)
else:
    print("DataFrame is empty, cannot create the map.")