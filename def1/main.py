"""
    Main module for the 'Project Bianchini Agroclimatology.'

    This module orchestrates the entire project workflow, including creating the project directory,
    checking and downloading the dataset, extracting relevant information, and visualizing the results through a dashboard.

    Args:
        None

    Returns:
        None
"""


import os
import dash
from download_data import dataset_check_download
from elaborate_data import extract_subfile
from dash_tot import create_dash



def create_project_directory(project_path, input_folder, output_folder):
    
    # Create the 'Project' directory on the Desktop if it doesn't exist
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print("'Project' directory created on the Desktop.")
    else:
        print("'Project' directory already exists on the Desktop.")

    input_path = os.path.join(project_path, input_folder)
    output_path = os.path.join(project_path, output_folder)

    # Create 'input' and 'output' subdirectories inside 'Project'
    if not os.path.exists(input_path):
        os.makedirs(input_path)
        print("'input' subdirectory created.")
    else:
        print("'input' subdirectory already exists.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print("'output' subdirectory created.")
    else:
        print("'output' subdirectory already exists.")

    return input_path, output_path


def read_config():
    try:
        # Try to read from the config file
        with open("config.txt", "r") as file:
            lines = file.readlines()
        
        # Parse the values from the file
        driver_path = lines[0].strip()
        binary_location = lines[1].strip()

    except FileNotFoundError:
        print('Nothing found')
        

    return driver_path, binary_location

def main():
    # Create the workspace
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    project_path = os.path.join(desktop, 'Project Bianchini Agroclimatology')

    input_folder = "input"
    output_folder = "output"

    input_folder_path, output_folder_path = create_project_directory(project_path, input_folder, output_folder)

    # url of the dataset
    url = 'https://www.kaggle.com/datasets/hugovallejo/' \
      'agroclimatology-data-of-the-state-of-paran-br/data'
    
    # Read user configuraion in file config.txt
    driver_path, binary_location = read_config()
    
    # Look for the dataset: it is dowloaded, it is updated, eventually download it
    dataset_check_download(url, input_folder_path, output_folder_path, driver_path, binary_location)

    # Adjust the dataset by extracting a subfile with interested information
    df, df_soja = extract_subfile(input_folder_path, output_folder_path)
 
    # Create a dashboard to visualize the resut
    app = create_dash(df, df_soja)
    
    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader = False)


if __name__ == "__main__":
    main()    
