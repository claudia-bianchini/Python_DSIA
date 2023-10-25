import pandas as pd
import folium
from matplotlib import colors as mcols
from branca.colormap import LinearColormap
from collections import defaultdict

# For the dashboard
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# # For the cursor
# from folium import CustomPane
# custom_pane = CustomPane(html='Custom Control', position='topright')
# map.get_root().add_child(custom_pane)

def rename_col(dataframe, rename_dictionary):
    """
    Rinomina le colonne di un 
    DataFrame utilizzando un dizionario di mappatura.

    Args:
        dataframe (pd.DataFrame): Il DataFrame da rinominare.
        dizionario_rinomina (dict): Un dizionario che mappa i nomi delle colonne originali ai nuovi nomi.

    Returns:
        pd.DataFrame: Il DataFrame con le colonne rinominate.
    """
    return dataframe.rename(columns=rename_dictionary)



def assign_date(dataframe):
# Make sure the date column is in datetime format
    dataframe['year'] = dataframe['data'].astype(str).str[:4]
    dataframe['month'] = dataframe['data'].astype(str).str[4:6]
    dataframe['day'] = dataframe['data'].astype(str).str[6:8]

    return dataframe

def add_column(df, df_soja):
    #Add to the Filtered Dataframe another column with the name of the minicipal
    df['name_ibge'] = ''    #Initialize the 'name_ibge' column
    # df['production'] = ''

    for df_index, df_row in df.iterrows():
        for soja_index, soja_row in df_soja.iterrows():
            if df_row['codigo_ibge'] == soja_row['codigo_ibge']:
                df.at[df_index, 'name_ibge'] = soja_row['name']
                # specific_df.at[df_index, 'production'] = soja_row['2016']
                
    return df

# Define a colormap with a continuous scale of colors

def color_scale(dataframe, var):
    # Group the DataFrame by 'latitude' and 'longitude' and calculate the mean of 'var'
    #grouped_data = dataframe.groupby(['latitude', 'longitude'])[var].mean().reset_index()

    # Create a LinearColormap with colors 'yellow', 'orange', and 'red' based on the range of 'var' means
    colormap = LinearColormap(['yellow', 'orange', 'red'], vmin=dataframe[var].min(), vmax=dataframe[var].max())

    # Create a dictionary to store colors for each unique pair of 'latitude' and 'longitude'
    color_dict = defaultdict(str)
    for index, row in dataframe.iterrows():
        color = colormap(row[var])
        # Store the color as a string in the format 'rgb(xxx,xxx,xxx)'
        color_dict[(row['latitude'], row['longitude'])] = color

    return [color_dict, colormap]


def create_dash_app(df, subdata_unique_coord, color_dict, colormap):
    # Initialize the Dash app
    app = dash.Dash(__name__, suppress_callback_exceptions=True)  # Create the Dash app with suppression of callback exceptions

    # Define the layout of the dashboard
    app.layout = html.Div([
        html.H1("Year Input"),
        # html.Div([
        #     html.Label("Choose a year"),
        #     options=[{'label': col, 'value': col} for col in unique_years.columns],
        #     dcc.Input(id="year-input", type="text", placeholder = 'Enter a year')
        # ]),
        # Dropdown to select a variable
        dcc.Dropdown(
            id='years-dropdown',
            options=[{'label': '2016', 'value' : '2016'}, 
                    {'label': '2017', 'value' : '2017'},
                    {'label': '2018', 'value' : '2018'}],
            value='2016'    # Set the default value
            ),

        # Map component
        # dcc.Graph(id='map'),
        # html.Div(id='map-container'),
        # Placeholder Graph component
        # dcc.Graph(id='map'),
        # HTML iframe to display the Folium map
        html.Iframe(id='map-iframe', width='100%', height='600')
    ])
    # Callback to update the map based on the input
    # @app.callback(
    #     Output("map-container", "children"),
    #     Input("year-input", "value"),
    #     #Input("longitude-input", "value"),
    # )
    @app.callback(
        Output('map-iframe', 'srcDoc'), #, 'figure')],
        [Input('years-dropdown', 'value')]
    )

    def update_map(year):
        # Get the selected year from the callback context
        year = dash.callback_context.triggered[0]['prop_id'].split('.')[0] 

        # Create a folium map centered around the first unique pair
        if not subdata_unique_coord.empty:
            m = folium.Map(
                location=[df.iloc[1]['latitude'], df.iloc[1]['longitude']],
                zoom_start=6
                )
            # Draw circles for the unique pairs on the map
            # print('Let\'s draw')
            for index, row in subdata_unique_coord.iterrows():
                unique_pair = (row['latitude'], row['longitude'])
                color = color_dict.get(unique_pair, 'blue') # Provide a default color if needed
                folium.CircleMarker(
                    location= unique_pair,  #(row['latitude'], row['longitude']),
                    name = 'Paranà - Brasil',
                    popup=f"Average TS: TROVA TEMP MEDIA °C, Productivity:", # {row['production']}", # Latitude: {row['latitude']} Longitude: {row['longitude']}",
                    tooltip='name_ibge', #f"{row['name_ibge']}",
                    radius= 10, #row['production']/500,  # Radius in meters
                    color=color, #(value for key, value in color.items() if key == row['codigo_ibge']),
                    fill=True,
                    fill_color = color, #(value for key, value in color.items() if key == row['codigo_ibge']),
                    fill_opacity = 0.2,
                    line_opacity = 0.8,         
                ).add_to(m)

            # Add the colormap to the map
            colormap.add_to(m)
            # Add a comment to the caption
            colormap.caption = f'Average Skin Earth temperature \'TS\' in  [°C]'

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
            

        
        else:
            print("DataFrame is empty, cannot create the map.")


        # Convert the Folium map to an HTML string
        map_html = m.get_root().render()
        # print(map_html)
        return map_html # [html.Div([dcc.Markdown(map_html)])]
    return app


# Define a function to update CircleMarker sizes on zoom
def update_circle_sizes(e):
    zoom_level = e['target'].zoom
    if zoom_level in circle_sizes:
        circle_size = circle_sizes[zoom_level]
        for feature in m.get_instantiate_features():
            if isinstance(feature, folium.CircleMarker):
                feature.radius = circle_size

def main():
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

    # Assign dates
    df = assign_date(df)

    
    # Create a subdataset with unique coordinates to allow a faster creation of the map
    subdata_unique_coord = df[['codigo_ibge', 'latitude', 'longitude']]
    subdata_unique_coord = subdata_unique_coord.drop_duplicates(subset=['codigo_ibge'])
    
    # Add a column with the name
    subdata_unique_coord = add_column(subdata_unique_coord, df_soja)
    # Define parameter for the map realization
    # Define a color scale scale 

    [color_dict, colormap] = color_scale(df, 'TS')

    # Ensure the 'name_ibge' column is of data type str
    subdata_unique_coord['name_ibge'] = subdata_unique_coord['name_ibge'].str.strip()

    # Dashboard:
    app = create_dash_app(df, subdata_unique_coord, color_dict, colormap)
    app.run_server(debug=True)
         
    #print(sum(specific_df['production']))


if __name__ == '__main__':
    main()