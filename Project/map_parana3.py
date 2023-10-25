import pandas as pd
import folium
from matplotlib import colors as mcols
from branca.colormap import LinearColormap
from collections import defaultdict

# For the cursor
from ipywidgets import interact, IntSlider, interactive, Output
import matplotlib.pyplot as plt
from IPython.display import display, clear_output

def assign_date(dataframe):
# Make sure the date column is in datetime format
    dataframe['year'] = dataframe['data'].astype(str).str[:4]
    dataframe['month'] = dataframe['data'].astype(str).str[4:6]
    dataframe['day'] = dataframe['data'].astype(str).str[6:8]

    return dataframe


def update_map(selected_year):
        # Filter the dataset for the selected year
        filtered_data = dataset[dataset['Year'] == selected_year]

        # Create a map with Folium
        m = folium.Map(location=[your_lat, your_lon], zoom_start=your_initial_zoom)

        # Add your map markers or custom visualization based on the filtered data
        # For example:
        for index, row in filtered_data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row['YourPopupContent'],
            ).add_to(m)

        with output_widget:
            clear_output(wait=True)
            display(m)

# Define a colormap with a continuous scale of colors

def color_scale(dataframe, var, year):
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

    return [color_dict, colormap]


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



# Define a function to update CircleMarker sizes on zoom
def update_circle_sizes(e):
    zoom_level = e['target'].zoom
    if zoom_level in circle_sizes:
        circle_size = circle_sizes[zoom_level]
        for feature in m.get_instantiate_features():
            if isinstance(feature, folium.CircleMarker):
                feature.radius = circle_size


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
[color_dict, colormap] = color_scale(specific_df, 'TS', year)

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
    m = folium.Map(
        location=[specific_df.iloc[1]['latitude'], specific_df.iloc[1]['longitude']],
        zoom_start=7
        )
    # Draw circles for the unique pairs on the map
    print('Let\'s draw')
    for index, row in specific_df.iterrows():
        unique_pair = (row['latitude'], row['longitude'])
        color = color_dict.get(unique_pair, 'blue') # Provide a default color if needed
        folium.CircleMarker(
            location= unique_pair,  #(row['latitude'], row['longitude']),
            name = 'Paranà - Brasil',
            popup=f"Average TS: TROVA TEMP MEDIA °C, Productivity: {row['production']}", # Latitude: {row['latitude']} Longitude: {row['longitude']}",
            tooltip=f"{row['name_ibge']}",
            radius= row['production']/500,  # Radius in meters
            color=color, #(value for key, value in color.items() if key == row['codigo_ibge']),
            fill=True,
            fill_color = color, #(value for key, value in color.items() if key == row['codigo_ibge']),
            fill_opacity = 0.2,
            line_opacity = 0.8,         
        ).add_to(m)

    # #Widget:
    # # Create an Output widget to display the map
    # output_widget = Output()
    # # Get unique years from the dataset
    # unique_years = specific_df['year'].unique()
    
    # # Create an interactive year selection slider
    # year_slider = IntSlider(
    #     value=min(unique_years),
    #     min=min(unique_years),
    #     max=max(unique_years),
    #     step=1,
    #     description='Select Year:',
    # )
    # # Connect the slider to the update_map function
    # interactive_plot = interactive(update_map, selected_year=year_slider)
    # output_widget.clear_output(wait=True)

    

    # # Display the year selection widget and map
    # display(year_slider, output_widget)

    # Ottieni gli anni unici dal dataset
    unique_years = sorted(specific_df['year'].unique())
    # Crea uno slider interattivo per la selezione dell'anno
    interact(update_map, selected_year=IntSlider(value=min(unique_years), min=min(unique_years), max=max(unique_years)))

    # # Add a ZoomControl to the map
    # m.add_child(folium.plugins.ZoomControl())


    # Bind the update_circle_sizes function to the zoom event
    # m.get_root().html.add_child(folium.Element('<div id="map" style="width:100%;height:100%;"></div>'))
    # m.get_root().script.add_child(folium.Element("document.getElementById('map').onmouseover = function() {"
    # "map.scrollWheelZoom.enable();"
    # "map.on('zoomend', function(e) {"
    # "var target = document.getElementById('map');"
    # "var zoom_level = target._leaflet_map.getZoom();"
    # "window.update_circle_sizes({ target: target, zoom: zoom_level });"
    # "});"
    # "};"))

    # Add the colormap to the map
    colormap.add_to(m)
    # Add a comment to the caption
    colormap.caption = f'Average Skin Earth temperature \'TS\' in {year} [°C]'

    # Define a custom HTML legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; z-index:1000; background-color: white; padding: 10px; border: 1px solid grey;">
        <p><strong>Legend</strong></p>
        <p>CircleMarker Radius:</p>
        <p style="font-size: 12px;">Radius is proportional to Productivity.</p>
    </div>
    """

    # Add the custom HTML legend to the map
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.map.LayerControl('topleft', collapsed= False).add_to(m)
    
    # Save the map to an HTML file
    m.save(map_path)

else:
    print("DataFrame is empty, cannot create the map.")

#print(sum(specific_df['production']))




    # # Display the year selection widget and map
    # display(year_slider, output_widget)
