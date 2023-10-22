# import selenium
# print(selenium.__version__)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set the path to the ChromeDriver executable
chrome_driver_path = "C:\\Users\\claud\\Documents\\Chromedriver"  # Path to your ChromeDriver executable

# Create ChromeOptions and add the ChromeDriver path
options = webdriver.ChromeOptions()
options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Path to your Chrome browser executable

# Set the executable path for ChromeDriver using the PATH environment variable
webdriver_path = "C:\\Path\\To\\ChromeDriver\\chromedriver.exe"  # Path to your ChromeDriver executable

# Set the PATH environment variable to the ChromeDriver executable path
import os
os.environ["PATH"] = f"{os.environ['PATH']};{webdriver_path}"

# Create a Chrome WebDriver instance with options
driver = webdriver.Chrome(options=options)

# URL of the webpage with the dataset
url = 'https://www.kaggle.com/datasets/hugovallejo/agroclimatology-data-of-the-state-of-paran-br/data'

# Open the URL
driver.get(url)

# You might need to wait for the content to load, as it's dynamically generated
wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed

try:
    target_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > span > span:nth-child(2) > span')))
    data = target_element.text
    print(data)
except:
    print('Element not found or timed out')

# Close the browser
driver.quit()
