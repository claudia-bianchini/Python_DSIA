import os

# from elaborate_data import extract_subfile
# from dashboard import crete_dash
# from download_data import ...



def main():
    # Create the workspace

    # Create a folder on Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    # Name of the folder
    folder_name = "Project Bianchini"
    project_path = os.path.join(desktop_path, folder_name)

    # Counter if there are folder with the same name
    counter = 1
    while os.path.exists(project_path):
        folder_name = f"Project Bianchini_{counter}"
        project_path = os.path.join(desktop_path, folder_name)
        counter += 1

    # Create new folder
    os.makedirs(project_path)

    # Create sub-folder 'output' e 'input' in 'Project Bianchini'
    output_folder = os.path.join(project_path, 'output')
    input_folder = os.path.join(project_path, 'input')

    os.makedirs(output_folder)
    os.makedirs(input_folder)


    # Download dataset if not already in the correct folder




    # # Adjust the dataset by extracting a subfile with interested information
    # extract_subfile()


    # # Create a dashboard to visualize the resut
    # create_dash()







if __name__ == "__main__":
    main()    
