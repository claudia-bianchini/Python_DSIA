import pandas as pd
import folium
from matplotlib import colors as mcols
from branca.colormap import LinearColormap
from collections import defaultdict

def assign_date(dataframe):
# Make sure the date column is in datetime format
    dataframe['year'] = dataframe['data'].astype(str).str[:4]
    dataframe['month'] = dataframe['data'].astype(str).str[4:6]
    dataframe['day'] = dataframe['data'].astype(str).str[6:8]

    return dataframe


# Define a colormap with a continuous scale of colors
def color_scale(dataframe, var, year):
    dataframe = dataframe.groupby(['codigo_ibge'])
    average_var = (dataframe['codigo_ibge'], dataframe[var].mean())
    colormap = LinearColormap(['yellow', 'orange', 'red'], vmin=min(average_var, key=lambda x: x[1]), vmax=max(average_var, key=lambda x: x[1]))
    
    #average_var = dataframe.groupby(['latitude', 'longitude'])[var].mean()
    #colormap = LinearColormap(['yellow', 'orange', 'red'], vmin=average_var.min(), vmax=average_var.max())

    # We have to create a dictionary because 'LinearColormap' is not natively JSON serializable
    #color_dict = {value: colormap(value) for value in average_var}
    color_dict = defaultdict(list)
    for item in average_var:
        color_dict[item[0]].append(item[1])
    
    return color_dict


def color_scale2(dataframe, var, year):
    # Group the DataFrame by 'latitude' and 'longitude' and calculate the mean of 'var'
    grouped_data = dataframe.groupby(['latitude', 'longitude'])[var].mean().reset_index()

    # Create a LinearColormap with colors 'yellow', 'orange', and 'red' based on the range of 'var' means
    colormap = LinearColormap(['yellow', 'orange', 'red'], vmin=grouped_data[var].min(), vmax=grouped_data[var].max())

    # Create a dictionary to store colors for each unique pair of 'latitude' and 'longitude'
    color_dict = defaultdict(str)
    for index, row in grouped_data.iterrows():
        color = colormap(row[var])
        # Store the color as a string in the format 'rgb(xxx,xxx,xxx)'
        color_dict[(row['latitude'], row['longitude'])] = color

    return color_dict


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



# Define parameter for the map realization
# Define a color scale scale 
color_dict = color_scale2(specific_df, 'TS', year)




# Unique coordinates
specific_df = specific_df.drop_duplicates(subset=['latitude', 'longitude'])

#Add to the Filtered Dataframe another column with the name of the minicipal
specific_df['name_ibge'] = ''    #Initialize the 'name_ibge' column
specific_df['production'] = ''

for df_index, df_row in specific_df.iterrows():
    try:
        for soja_index, soja_row in df_soja.iterrows():
            if df_row['codigo_ibge'] == soja_row['codigo_ibge']:
                specific_df.at[df_index, 'name_ibge'] = soja_row['name']
                specific_df.at[df_index, 'production'] = soja_row['2016']
                pass
    except: pass

# Ensure the 'name_ibge' column is of data type str
specific_df['name_ibge'] = specific_df['name_ibge'].str.strip()


# Create a folium map centered around the first unique pair

if not specific_df.empty:
    m = folium.Map(location=[specific_df.iloc[1]['latitude'], specific_df.iloc[1]['longitude']], zoom_start=10)

    # Draw circles for the unique pairs on the map
    for index, row in specific_df.iterrows():
        unique_pair = (row['latitude'], row['longitude'])
        color = color_dict.get(unique_pair, 'blue') # Provide a default color if needed
        folium.CircleMarker(
            location= unique_pair,  #(row['latitude'], row['longitude']),
            popup=f"{row['name_ibge']}, Latitude: {row['latitude']} Longitude: {row['longitude']}",
            radius= row['production']/500,  # Radius in meters
            color=color, #(value for key, value in color.items() if key == row['codigo_ibge']),
            fill=True,
            fill_color=color, #(value for key, value in color.items() if key == row['codigo_ibge']),
            fill_opacity = 0.2           
        ).add_to(m)

    # Save the map to an HTML file
    m.save(map_path)
else:
    print("DataFrame is empty, cannot create the map.")