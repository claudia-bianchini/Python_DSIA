import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import folium
import dash_folium


# Define a function to create the map
def create_map(df, color_dict, colormap):
    if not df.empty:
        m = folium.Map(
            location=[df.iloc[0]['latitude'], df.iloc[0]['longitude']],  # Use the first row's coordinates
            zoom_start=7
        )
        
        for index, row in df.iterrows():
            unique_pair = (row['latitude'], row['longitude'])
            color = color_dict.get(unique_pair, 'blue') # default value if something doen't work
            
            folium.CircleMarker(
                location=unique_pair,
                name='Paranà - Brasil',
                popup=f"Average TS: TROVA TEMP MEDIA °C, Productivity: {row['production']}",
                tooltip=f"{row['name_ibge']}",
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.2,
                line_opacity=0.8,
            ).add_to(m)

        # Add the colormap to the map
        colormap.add_to(m)
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
        folium.map.LayerControl('topleft', collapsed=False).add_to(m)

    else:
        print("DataFrame is empty, cannot create the map.")
    
    return m



# Define the main function
def main():
    # Import data
    path_filtered_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
    df = pd.read_csv(path_filtered_data)
    
    path_soja_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\input\produtividade_soja.csv'
    df_soja = pd.read_csv(path_soja_data)


    # Unique coordinates
    subdata_unique_coord = df[['name_ibge', 'latitude', 'longitude']].drop_duplicates(subset=['name_ibge'])

    # Create a color scale
    color_dict, colormap = color_scale(df, 'TS')

    # Create the map
    m = create_map(subdata_unique_coord, color_dict, colormap)

    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Define the layout of the dashboard
    app.layout = html.Div([
        html.H1("Dashboard with Map"),

        # Dropdown to select a variable
        dcc.Dropdown(
            id='variable-dropdown',
            options=[{'label': col, 'value': col} for col in unique_years.columns],
            value='years'
        ),

        # Map component
        dcc.Graph(id='map'),

        # # Plotly chart
        # dcc.Graph(id='chart')
    ])

    # Callback to update the map and chart based on the selected variable
    @app.callback(
        [Output('map', 'figure')], # , Output('chart', 'figure')],
        [Input('choose a year', 'years')]
    )
    
    def update_map_and_chart(selected_variable):
        # Update the map here with the selected variable
        # You need to replace this with your specific logic

        # Update the chart here with the selected variable
        # You need to replace this with your specific logic

    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)


if __name__ == '__main__':
    main()








































# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import plotly.express as px
# import pandas as pd
# import folium
# import dash_folium


# def create_map(df, color_dict, colormap): 
#     # Create a folium map centered around the first unique pair
#     if not df.empty:
#         m = folium.Map(
#             location=[df.iloc[1]['latitude'], df.iloc[1]['longitude']],
#             zoom_start=7
#             )
#         # Draw circles for the unique pairs on the map
#         print('Let\'s draw')
#         for index, row in df.iterrows():
#             unique_pair = (row['latitude'], row['longitude'])
#             color = color_dict.get(unique_pair, 'blue') # Provide a default color if needed
#             folium.CircleMarker(
#                 location= unique_pair,  #(row['latitude'], row['longitude']),
#                 name = 'Paranà - Brasil',
#                 popup=f"Average TS: TROVA TEMP MEDIA °C, Productivity: {row['production']}", # Latitude: {row['latitude']} Longitude: {row['longitude']}",
#                 tooltip=f"{row['name_ibge']}",
#                 radius= 10, #row['production']/500,  # Radius in meters
#                 color=color, #(value for key, value in color.items() if key == row['codigo_ibge']),
#                 fill=True,
#                 fill_color = color, #(value for key, value in color.items() if key == row['codigo_ibge']),
#                 fill_opacity = 0.2,
#                 line_opacity = 0.8,         
#             ).add_to(m)

#         # Add the colormap to the map
#         colormap.add_to(m)
#         # Add a comment to the caption
#         colormap.caption = f'Average Skin Earth temperature \'TS\' in  [°C]'

#         # Define a custom HTML legend
#         legend_html = """
#         <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; z-index:1000; background-color: white; padding: 10px; border: 1px solid grey;">
#             <p><strong>Legend</strong></p>
#             <p>CircleMarker Radius:</p>
#             <p style="font-size: 12px;">Radius is proportional to Productivity.</p>
#         </div>
#         """

#         # Add the custom HTML legend to the map
#         m.get_root().html.add_child(folium.Element(legend_html))

#         folium.map.LayerControl('topleft', collapsed= False).add_to(m)
        

    
#     else:
#         print("DataFrame is empty, cannot create the map.")


#     return m



# def main():
# #  Import data
#     path_filtered_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
#     df = pd.read_csv(path_filtered_data)
    
#     path_soja_data = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\input\produtividade_soja.csv' #here there are the name of the municipal
#     df_soja = pd.read_csv(path_soja_data)

#     #We need ro rename the column:
#     colums_rename = {'nivel ': 'nivel', 'codigo_ibge ': 'codigo_ibge', 'name                        ': 'name',
#                         '2004   ' : '2004', '2005   ' : '2005', '2006   ' : '2006', '2007   ' : '2007', '2008   ': '2008', 
#                         '2009   ' : '2009', '2010   ' : '2010', '2011   ' : '2011', '2012   ' : '2012', '2013   ' : '2013', 
#                         '2014   ' : '2014', '2015   ' : '2015', '2016   ' : '2016', '2017' : '2017'}
    
#     df_soja = rename_col(df_soja, colums_rename)

#     # Unique coordinates to allow a faster creation of the map
#     subdata_unique_coord = df[['name_ibge', 'latitude', 'longitude']]
#     subdata_unique_coord = subdata_unique_coord.drop_duplicates(subset=['name_ibge'])



#     # Define the path to the output folder
#     output_folder = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output'
#     map_path = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\map.html'

#     # Assign dates
#     df = assign_date(df)
#     print('date assigned')

#     dashboard = create_dash(df)


# def crete_dash(data):
#     # Initialize the Dash app
#     app = dash.Dash(__name__)

#     # Define the layout of the dashboard
#     app.layout = html.Div([
#         html.H1("Dashboard with Map"),
        
#         # # Dropdown to select a variable
        
#         # # Get unique values from the 'year' column
#         # data = pd.DataFrame(data)
#         # unique_years = data['year'].unique()

#         # dcc.Dropdown(
#         #     id='years',
#         #     options=[{'label': col, 'value': col} for col in unique_years.columns],
#         #     value='years'
#         # ),
        
#         # Map component
#         dcc.Graph(id='map'),

#         # Plotly chart
#         # dcc.Graph(id='chart')
#     ])

#     # Callback to update the map and chart based on the selected variable
#     @app.callback(
#         [Output('map', 'figure')],   # , Output('chart', 'figure')],
#         [Input('variable-dropdown', 'value')]
#     )





# def update_map_and_chart(selected_variable):
#     # Create a map

#     m = create_map(subdata_unique_coord, color_dict, colormap)

#     # Create a Plotly chart
#     # fig = px.scatter(data, x='x_column', y='y_column', color=selected_variable)

#     return dash_folium.Figure(fig), fig




# # Run the app
# if __name__ == '__main__':
#     app.run_server(debug=True)
