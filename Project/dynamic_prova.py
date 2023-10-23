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

import time


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
        css_selector = '#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > span > span:nth-child(2) > span'
        target_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        data = target_element.text
        
        print(data)

    except:
        print('Element not found or timed out')

    if data:
        check_last_update(data, url, driver)
    # Close the browser
    driver.quit()
    

            
def check_last_update(update_date, url, driver):    
    try:
        with open("output\\last_update.txt", "r") as file:
            last_checked_date = file.read()
        
        if update_date and update_date != last_checked_date:
            print('Dataset is updated. Downloading the new version.')
            download_dataset(url, driver)
            # Update the last checked date
            with open("output\\last_update.txt", "a") as file:  # Use "w" mode to overwrite the content
                file.write(update_date)
            
        else:
            print('Dataset is not updated. No need to download.')
            
    except FileNotFoundError:
        with open("output\\last_update.txt", "w") as file:
            file.write(update_date)
            download_dataset(url, driver)
            

    

def download_dataset2(url, driver):
    #To dowload the dataset you need to log in
    # username = "your_username"
    # password = "your_password"

    # Define the local file path where you want to save the dataset
    local_directory = "input"
    local_file_path = os.path.join(local_directory, "downloaded_dataset.zip")

    # Create the directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    driver.get(url)

    # # Sign in:


    # sign_in_button = "#site-container > div > div.sc-kKQOHL.dyrYTA > div.sc-iGtWQ.hQbRdM > div.sc-cmtnDe.djqpYo > div > div:nth-child(1) > a > button"
    
    # username_field = driver.find_element(By.ID, "claudia.bianchini@edu.esiee.fr")  # Adjust the locator as needed
    # password_field = driver.find_element(By.ID, "HBjv93h6gF4")  # Adjust the locator as needed

    # username_field.send_keys("claudia.bianchini@edu.esiee.fr")
    # password_field.send_keys('HBjv93h6gF4')

    # Locate the download button using a CSS selector
    # try:
    css_selector = "#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > div > a > button"
    #download_button = driver.find_element(By.CSS_SELECTOR, css_selector)

    # Wait for the download button to become clickable
    wait = WebDriverWait(driver, 20)
    download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

    # Click the download buttom
    download_button.click()
    # Wait for the new page to open
    wait = WebDriverWait(driver, 10)
    wait.until(EC.new_window_is_opened(driver.window_handles))
    
    # Now you are on the new page
    new_page_url = driver.current_url
    print("You are on the new page: Sign In", new_page_url)

    # Select enter with google
    gmail_selector = "#site-content > div.sc-bIlklX.hkWNaR > div > div.sc-fjicLR.fFKoLg > form > div > div > div.sc-jvCgnh.lclGyk > button:nth-child(1) > span.sc-gjTGSA.sc-eACynP.jTTdyU.ctdVmt"
    # Wait for the download button to become clickable
    wait = WebDriverWait(driver, 20)
    gmail_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, gmail_selector)))
    # Click the sign in with Google buttom
    download_button.click()
    
    # Aspetta fino a quando il file è stato scaricato (puoi controllare il nome del file, la directory di download, ecc.)
    wait = WebDriverWait(driver, 120)  # Imposta un timeout massimo in secondi
    try:
        # Sostituisci 'Nome_Del_File_Scaricato.zip' con il nome del file che aspetti di scaricare
        wait.until(EC.presence_of_element_located((By.XPATH, f'//a[contains(text(), "archive.zip")]')))
        print("Il dataset è stato scaricato con successo.")
    except Exception as e:
        print("Si è verificato un errore durante il download del dataset:", e)


#     # Sign in: enter e-mail and pssw
#     username = 'claudia.bianchini@edu.esiee.fr'
#     password = 'HBjv93h6gF4'
#     # username_field = driver.find_element(By.ID, "claudia.bianchini@edu.esiee.fr")  # Adjust the locator as needed
#     # password_field = driver.find_element(By.ID, "HBjv93h6gF4")  # Adjust the locator as needed

# # username_field.send_keys("claudia.bianchini@edu.esiee.fr")
# # password_field.send_keys('HBjv93h6gF4')
#     link_sign_selector = "#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > span > section > div > div > div > div > ul > li.JDAKTe.eARute.W7Aapd.zpCp3.SmR8 > div"
#     link = driver.find_element(By.CSS_SELECTOR, link_sign_in)
#     link.click()

#     #Insert your email:
#     username_selector = "#identifierId" 
#     username_input = driver.find_element(By.ID, username_selector)
#     username_input.send_keys(username)

#     submit_us_selector = "#identifierNext > div > button"
#     submit_us_button = driver.find_element(By.ID, submit_us_selector)
#     submit_us_button.click()

#     #Insert your password:
#     password_selector = "#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input"
#     password_input = driver.find_element(By.ID, password_selector)
#     password_input.send_keys(password)

#     submit_pssw_selector = "#passwordNext > div > button"
#     submit_pssw_button = driver.find_element(By.ID, submit_pssw_selector)
#     submit_pssw_button.click()


    # Wait for a few seconds (adjust as needed)
    driver.implicitly_wait(120)
    # Close the WebDriver
    driver.quit()
    print("Dataset downloaded and saved to:", local_file_path)
    # except: 
        # print("Failed to download the dataset")



def download_dataset3(dataset_url, driver):
    # Initialize the Chrome WebDriver
    username = 'claudia.bianchini@edu.esiee.fr'
    password = 'HBjv93h6gF4'

    download_path = '\\input'
     # Create the directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)
    try:
        # Open Kaggle and log in
        driver.get('https://www.kaggle.com/account/login')
        driver.find_element(By.ID, 'login').send_keys(username)
        driver.find_element_by_id(By.ID, 'password').send_keys(password)
        driver.find_element_by_name(By.NAME, 'submit').click()

        # Navigate to the dataset page
        driver.get(dataset_url)

        # Click the download button (modify the selector as needed)
        css_selector = "#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > div > a > button"
        download_button = driver.find_element(By.CSS_SELECTOR, css_selector)
        download_button.click()

        # Wait for the file to be downloaded
        timeout = 200  # Adjust as needed
        while timeout > 0:
            if any(fname.startswith('kaggle.json') for fname in os.listdir(download_path)):
                print('Dataset downloaded successfully.')
                break
            time.sleep(1)
            timeout -= 1
        else:
            print('Timeout: The file was not downloaded within 60 seconds.')
    except Exception as e:
        print(f'Error: {str(e)}')
    finally:
        # Close the WebDriver
        driver.quit()

def download_dataset(dataset_url, driver):
    
    # Navigate to the Kaggle dataset page
    driver.get(dataset_url)

    # Define the local file path where you want to save the dataset
    local_directory = "input"
    local_file_path = os.path.join(local_directory, "downloaded_dataset.zip")

    # Selectors:
    download_button_selector = "#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > div > a > button"
    id_sign_in = "#site-container > div > div.sc-kKQOHL.dyrYTA > div.sc-iGtWQ.hQbRdM > div.sc-cmtnDe.djqpYo > div > div:nth-child(1) > a > button"
    #id_sign_in = "#site-container > div > div.sc-kKQOHL.dyrYTA > div.sc-iGtWQ.hVthTE > div.sc-cmtnDe.djqpYo > div > div:nth-child(1) > a > button"
    #id_sign_in = "#site-container > div > div.sc-kKQOHL.dyrYTA > div.sc-iGtWQ.hVthTE > div.sc-cmtnDe.djqpYo > div > div:nth-child > a > button"
    # id_sign_in = "#site-container > div > div.sc-kKQOHL.dyrYTA > div.sc-iGtWQ.hVthTE > div.sc-cmtnDe.djqpYo > div > div:nth-child(1) > a > button"
    # Check if the user is logged in by looking for a sign-out button
    try:
        # If the user is already logged in, we won't see the login form
        login_form = driver.find_element(By.ID, id_sign_in)
        # EC.element_to_be_clickable((By.ID, id_sign_in))
        #login_form = True
    except NoSuchElementException:
        login_form = None

    print(f'Devo accedere?', login_form)
    # If the login form is present, the user is not logged in
    if login_form:
        # Wait for the user to enter their username and password
        print("Please enter your Kaggle username and password.")
        # Wait for the new page to load (change the URL)
        # Click the sign in button
        login_form.click()

        new_page_url = r'https://www.kaggle.com/account/login?phase=startSignInTab&returnUrl=%2Fdatasets%2Fhugovallejo%2Fagroclimatology-data-of-the-state-of-paran-br'
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_to_be(new_page_url))

        while True:
            time.sleep(1)  # Wait for the user to log in manually
            print('Compiling...')
            # Check if the user is logged in by looking for the login form
            try:
                #login_form = driver.find_element(By.ID, id_sign_in) 
                dowload_form = driver.find_element(By.CSS_SELECTOR, download_button_selector)
                break
            except NoSuchElementException:
                # print('Wait')
                # If the login form is not found, the user is logged in
                pass

    # Now that the user is logged in or was already logged in, proceed to download the dataset
    # Wait for the "Download" button to become clickable
    # Click the download button (modify the selector as needed)
    print('Go on')
    
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, download_button_selector))
    )

    # Click the download button to initiate the download
    download_button.click()

    # At this point, the download process will vary based on your browser settings and OS

    # Wait for the file to appear in the download directory
    downloaded_file = None
    timeout = 480  # Maximum time to wait for the download
    start_time = time.time()

    while time.time() - start_time < timeout:
        # List files in the download directory
        files = os.listdir(local_directory)
        
        # Check if the desired file is in the directory
        if any(file.endswith('.zip') for file in files):
            # You can set some condition to verify that the file is fully downloaded
            downloaded_file = os.path.join(local_directory, [file for file in files if file.endswith('.zip')][0])
            break
        
        # Sleep for a short interval before checking again
        time.sleep(1)

    if downloaded_file:
        print(f"Download completed. File saved as: {downloaded_file}")
    else:
        print("Download didn't complete within the timeout.")

    # Close the browser when done
    driver.quit()




def main():

    # URL of the webpage with the dataset
    url = 'https://www.kaggle.com/datasets/hugovallejo/agroclimatology-data-of-the-state-of-paran-br/data'
    find_last_update(url)
    #print(type(data))
    


main()