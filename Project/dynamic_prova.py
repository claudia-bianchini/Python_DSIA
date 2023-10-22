# import selenium
# print(selenium.__version__)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from requests.auth import HTTPBasicAuth



def find_last_update(url):
    # Set the path to the ChromeDriver executable
    chrome_driver_path = "C:\\Users\\claud\\Documents\\Chromedriver"  # Path to your ChromeDriver executable

    # Create ChromeOptions and add the ChromeDriver path
    options = webdriver.ChromeOptions()
    options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Path to your Chrome browser executable

    # Set the executable path for ChromeDriver using the PATH environment variable
    webdriver_path = "C:\\Path\\To\\ChromeDriver\\chromedriver.exe"  # Path to your ChromeDriver executable

    # Set the PATH environment variable to the ChromeDriver executable path

    os.environ["PATH"] = f"{os.environ['PATH']};{webdriver_path}"

    # Create a Chrome WebDriver instance with options
    driver = webdriver.Chrome(options=options)

    # Open the URL
    driver.get(url)

    # You might need to wait for the content to load, as it's dynamically generated
    wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed
    #data = None
    try:
        target_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > span > span:nth-child(2) > span')))
        data = target_element.text
        
        print(data)

    except:
        print('Element not found or timed out')

    if data:
        check_last_update(data, url)
    # Close the browser
    driver.quit()
    

            
def check_last_update(update_date, url):
    try:
        with open("output\\last_update.txt", "r") as file:
            last_checked_date = file.read()
        
        if update_date and update_date != last_checked_date:
            print('Dataset is updated. Downloading the new version.')
            download_dataset(url)
            # Update the last checked date
            with open("output\\last_update.txt", "w") as file:  # Use "w" mode to overwrite the content
                file.write(update_date)
            
        else:
            print('Dataset is not updated. No need to download.')
            
    except FileNotFoundError:
        with open("output\\last_update.txt", "w") as file:
            file.write(update_date)
            download_dataset(url)
            file.write(update_date)

    


def download_dataset2(dataset_url):
    local_file_path = '\\input\\data.zip'
    response = requests.get(dataset_url)
    if response.status_code == 200:
        with open(dataset_file, 'wb') as file:
            file.write(response.content)
        print('Dataset downloaded successfully.')
    else:
        print('Failed to download the dataset:', response.status_code)


def download_dataset(dataset_url):
    #To dowload the dataset you need to log in
    # username = "your_username"
    # password = "your_password"

    response = requests.get(dataset_url)    #, auth=HTTPBasicAuth(username, password))

    # Define the local file path where you want to save the dataset
    local_file_path = "\\input\\downloaded_dataset.zip"

    # Send an HTTP GET request to the URL
    response = requests.get(dataset_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open the local file in binary write mode and write the response content to it
        with open(local_file_path, "wb") as file:
            file.write(response.content)
        print("Dataset downloaded and saved to:", local_file_path)
    else:
        print("Failed to download the dataset. HTTP Status Code:", response.status_code)





def main():

    # URL of the webpage with the dataset
    url = 'https://www.kaggle.com/datasets/hugovallejo/agroclimatology-data-of-the-state-of-paran-br/data'
    find_last_update(url)
    #print(type(data))
    


main()