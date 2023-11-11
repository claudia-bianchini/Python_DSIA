# import selenium
# print(selenium.__version__)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException 
import os
import requests
from requests.auth import HTTPBasicAuth
from selenium.common.exceptions import TimeoutException
import time

import zipfile

def find_last_update(url):

    local_directory = r'C:\Users\claud\Desktop\Python_project\input'
    chrome_driver_path = "C:/Users/claud/Documents/Chromedriver/chromedriver.exe"
    chrome_binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": local_directory
    }
    options.add_experimental_option("prefs", prefs)

    # Imposta il percorso del driver di Chrome usando ChromeOptions
    options.binary_location = chrome_binary_location
    os.environ["webdriver.chrome.driver"] = chrome_driver_path

    # Inizializza il driver di Chrome senza il parametro executable_path
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # You might need to wait for the content to load, as it's dynamically generated
    wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed
    data = None
    try:
        #css_selector = '#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > span > span:nth-child(2) > span'
        css_selector = '#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-kriKqB.bdptWe > div.sc-jIXSKn.bdYZfJ > span > span:nth-child(2) > span'
        target_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        data = target_element.text
        
        # print(data)

    except:
        print('Element not found or timed out')

    if data:
        check_last_update(data, url, driver, local_directory)
    # Close the browser
    # driver.quit()
    

            
def check_last_update(update_date, url, driver, local_directory):    
    try:
        with open("output\\last_update.txt", "r") as file:
            last_checked_date = file.read()
        
        if update_date and update_date != last_checked_date:
            print('Dataset is updated. Downloading the new version.')
            download_dataset(url, driver, local_directory)
            # Update the last checked date
            with open("output\\last_update.txt", "w") as file:  # Use "w" mode to overwrite the content
                file.write(update_date)
            
        else:
            print('Dataset is not updated. No need to download.')
            
    except FileNotFoundError:
        with open("output\\last_update.txt", "w") as file:
            file.write(update_date)
            download_dataset(url, driver, local_directory)
            



def download_dataset(dataset_url, driver, local_directory):
    # Delete all file in the directory
    for filename in os.listdir(local_directory):
        file_path = os.path.join(local_directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File {filename} rimosso con successo.")
            elif os.path.isdir(file_path):
                print(f"Il percorso {filename} è una directory. Non rimosso.")
        except Exception as e:
            print(f"C'è stato un errore nella rimozione di {filename}: {e}")

    # Set up for waiting:
    wait = WebDriverWait(driver, 30)

    # Selectors:
    download_button_selector = '#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-kriKqB.bdptWe > div.sc-jIXSKn.bdYZfJ > div > a > button > span'
    id_sign_in = '#site-container > div > div.sc-cmtnDe.WXA-DT > div.sc-lfeRdP.lgbEgp > div.sc-gglKJF.eeMhNC > div > div:nth-child(1) > a > button > span'
    
    # Check if the user is logged in by looking for a sign-out button
    wait.until(EC.url_to_be(dataset_url))
    # print('Let\'s try')
    try:
        # Wait for the login form to be visible
        login_form = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, id_sign_in)))
        # print('Login form is visible')
        
        # Click the login button
        login_form.click()
        print("Please enter your Kaggle username and password.")

        # Wait for the "Download" button to become clickable
        while True:
            time.sleep(1)  # Wait for the user to log in manually
            # print('Compiling...')
            # Check if the user is logged in by looking if the dowload button is avalible
            try:
                dowload_form = driver.find_element(By.CSS_SELECTOR, download_button_selector)
                break
            except NoSuchElementException:
                # print('Wait')
                pass

         
    except TimeoutException:
        print(f'Login form not found or not visible by selector: {id_sign_in}')
        login_form = None
        
    # Now that the user is logged in or was already logged in, proceed to download the dataset
    
    # print('Go on')
    
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, download_button_selector))
    )

    # Click the download button to initiate the download
    download_button.click()
    print('Download running...')

    # Wait for the file to appear in the download directory
    downloaded_file = None
    timeout = 48000  # Take about 80.2sec to dowload the file
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            files = os.listdir(local_directory)
            #print("Files in directory:", files)

            found_files = [file for file in files if file.endswith('.zip')]
            if found_files:
                downloaded_file = found_files[0]
                print('File with .zip extension found:', downloaded_file)
                unzip_file(local_directory, downloaded_file)    
                break
                # return downloaded_file

            # print("Current time:", time.time() - start_time)
        except Exception as e:
            print("Error occurred:", e)
            time.sleep(10)

    

    else:
        print("Download didn't complete within the timeout.")

    driver.quit()
    # return None


def unzip_file(directory, zip_file_name):
    zip_file_path = os.path.join(directory, zip_file_name)

    if not os.path.exists(zip_file_path):
        print(f"The specified .zip file '{zip_file_name}' does not exist in the directory.")
        return

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(directory)
        print(f"Successfully extracted '{zip_file_name}' in the directory: {directory}")
    
    except zipfile.BadZipFile:
        print(f"The file '{zip_file_name}' is not a valid .zip file.")
    
    except Exception as e:
        print(f"An error occurred while extracting '{zip_file_name}': {e}")


def main():

    # URL of the webpage with the dataset
    url = 'https://www.kaggle.com/datasets/hugovallejo/agroclimatology-data-of-the-state-of-paran-br/data'
    find_last_update(url)
    #print(type(data))
    


main()