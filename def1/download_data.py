"""
    Module for checking, downloading, and unzipping a dataset from a specified webpage.

    Args:
        url (str): URL of the webpage to check for the dataset.
        input_folder_directory (str): Local directory for downloads.
        output_folder_directory (str): Directory to store output data.
        chrome_driver_path (str): Path to the Chrome WebDriver.
        chrome_binary_location (str): Path to the Chrome binary.

    Returns:
        None
"""

import os
import time
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def initialize_driver(local_directory, chrome_driver_path, chrome_binary_location):
    """
    Initialize a Chrome WebDriver with custom settings.

    Args:
        local_directory (str): Local directory for downloads.
        chrome_driver_path (str): Path to the Chrome WebDriver.
        chrome_binary_location (str): Path to the Chrome binary.

    Returns:
        webdriver.Chrome: Instance of the Chrome WebDriver.
    """
    # Create ChromeOptions to customize browser behavior
    options = webdriver.ChromeOptions()
    # Set download directory for Chrome
    prefs = {
        "download.default_directory": local_directory
    }
    options.add_experimental_option("prefs", prefs)
    # Set the path to the Chrome binary location
    options.binary_location = chrome_binary_location
    # Set the path to the Chrome WebDriver
    os.environ["webdriver.chrome.driver"] = chrome_driver_path
    # Initialize Chrome WebDriver with the specified options
    driver = webdriver.Chrome(options=options)

    return driver


def find_last_update(url, driver):
    """
    Find the last update date on a webpage.

    Args:
        url (str): URL of the webpage to scrape.
        driver (webdriver.Chrome): Instance of the Chrome WebDriver.

    Returns:
        str: Last update date found on the webpage.
    """
    # Open the specified URL in the Chrome browser
    driver.get(url)
    # Set up a WebDriverWait instance with a timeout of 10 seconds
    wait = WebDriverWait(driver, 10)
    try:
        # Define the CSS selector for the target element containing the last update date
        css_selector = '#site-content > div:nth-child(2) > div > div > div.sc-kriKqB.bdptWe > div.sc-jIXSKn.bdYZfJ > span > span:nth-child(2) > span'       
        # Wait until the target element is present in the DOM
        target_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        # Return the text content of the target element (last update date)
        return target_element.text

    except TimeoutException:
        # If the target element is not found within the specified timeout, return None
        return None


def check_last_update(update_date, url, driver, input_directory, output_directory):
    """
    Check the last update date and download the dataset if it's updated.

    Args:
        update_date (str): Last update date of the dataset.
        url (str): URL of the webpage to check for the dataset.
        driver (webdriver.Chrome): Instance of the Chrome WebDriver.
        input_directory (str): Local directory for downloads.
        output_directory (str): Local directory to store the last update file.

    Returns:
        str: Name of the downloaded ZIP file.
    """
    # Define the filename for storing the last update date
    filename = 'last_update.txt'
    # Create the full path for the last update file
    last_update_path = os.path.join(output_directory, filename)
    try:
        # Try to open the last update file for reading
        with open(last_update_path, "r", encoding="utf-8") as file:
            # Read the last checked date from the file
            last_checked_date = file.read()
            zip_file_name = None
        # Check if the dataset is updated
        if update_date and update_date != last_checked_date:
            print('Dataset is updated. Downloading the new version.')
            zip_file_name = download_dataset(url, driver, input_directory)
            # Update the last update file with the new date
            with open(last_update_path, "w", encoding="utf-8") as file:
                file.write(update_date)
        else:
            print('Dataset is not updated. No need to download.')
    except FileNotFoundError:
        # If the last update file doesn't exist, create it and download the dataset
        with open(last_update_path, "w", encoding="utf-8") as file:
            file.write(update_date)
            zip_file_name = download_dataset(url, driver, input_directory)
    # Return the name of the downloaded ZIP file
    return zip_file_name



def download_dataset(dataset_url, driver, local_directory):
    """
    Download the dataset from a webpage.

    Args:
        dataset_url (str): URL of the webpage to download the dataset.
        driver (webdriver.Chrome): Instance of the Chrome WebDriver.
        local_directory (str): Local directory for downloads.

    Returns:
        str: Name of the downloaded ZIP file.
    """
    # Remove existing files in the local directory
    for filename in os.listdir(local_directory):
        file_path = os.path.join(local_directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File {filename} removed successfully.")
            elif os.path.isdir(file_path):
                print(f"Path {filename} is a directory. Not removed.")
        except Exception as e:
            print(f"Error in removing {filename}: {e}")

    # Wait for the dataset URL to be loaded
    wait = WebDriverWait(driver, 30)
    wait.until(EC.url_to_be(dataset_url))
    # Define CSS selectors for download button and sign-in button
    download_button_selector = '#site-content > div:nth-child(2) > div > div > div.sc-kriKqB.bdptWe > div.sc-jIXSKn.bdYZfJ > div > a > button'
    id_sign_in = '#site-container > div > div.sc-cmtnDe.WXA-DT > div.sc-lfeRdP.lgbEgp > div.sc-gglKJF.eeMhNC > div > div:nth-child(1) > a > button > span'
    try:
        # Attempt to locate the login form
        login_form = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, id_sign_in))
        )
        login_form.click()
        print("Please enter your Kaggle username and password.")
        # Wait for the download button to appear after sign-in
        while True:
            time.sleep(1)
            try:
                driver.find_element(By.CSS_SELECTOR, download_button_selector)
                break
            except NoSuchElementException:
                pass

    except TimeoutException:
        print(f'Login form not found or not visible by selector: {id_sign_in}')
        login_form = None

    # Click the download button
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, download_button_selector))
    )
    download_button.click()
    #print('Download running...')
    downloaded_file = None
    timeout = 480
    start_time = time.time()
    # Wait for the download to complete
    while time.time() - start_time < timeout:
        try:
            files = os.listdir(local_directory)
            found_files = [file for file in files if file.endswith('.zip')]
            if found_files:
                downloaded_file = found_files[0]
                print('File with .zip extension found:', downloaded_file)
                break
        except Exception as e:
            print("Error occurred:", e)
            time.sleep(10)
    else:
        print("Download didn't complete within the timeout.")

    # Quit the WebDriver
    driver.quit()
    # Return the name of the downloaded ZIP file
    return downloaded_file



def unzip_file(directory, zip_file_name):
    """
    Unzip a .zip file in the specified directory.

    Args:
        directory (str): Directory where the .zip file is located.
        zip_file_name (str): Name of the .zip file to be extracted.
    """
    zip_file_path = os.path.join(directory, zip_file_name)

    # Check if the specified .zip file exists
    if not os.path.exists(zip_file_path):
        print(f"The specified .zip file '{zip_file_name}' does not exist in the directory.")
        return

    try:
        # Extract the contents of the .zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(directory)
        print(f"Successfully extracted '{zip_file_name}' in the directory: {directory}")

    except zipfile.BadZipFile:
        print(f"The file '{zip_file_name}' is not a valid .zip file.")

    except Exception as e:
        print(f"An error occurred while extracting '{zip_file_name}': {e}")


def dataset_check_download(url, input_folder_directory, output_folder_directory, chrome_driver_path, chrome_binary_location):
    """
    Orchestrates the process of checking, downloading, and unzipping the dataset.

    Args:
        url (str): URL of the webpage to check for the dataset.
        input_folder_directory (str): Local directory for downloads.
        output_folder_directory (str): Directory to store output data.
        chrome_driver_path (str): Path to the Chrome WebDriver.
        chrome_binary_location (str): Path to the Chrome binary.

    Returns:
        None
    """
    # Initialize the Chrome WebDriver
    driver = initialize_driver(input_folder_directory, chrome_driver_path, chrome_binary_location)
    zip_file_name = None
    # Find the last update date
    data = find_last_update(url, driver)
    if data:
        # Check last update date and download the dataset if updated
        zip_file_name = check_last_update(data, url, driver, input_folder_directory, output_folder_directory)
    else:
        print('Element not found or timed out')
    if zip_file_name:
        # Unzip the downloaded dataset
        unzip_file(input_folder_directory, zip_file_name)
