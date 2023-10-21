import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
from html.parser import HTMLParser
from urllib.request import Request, urlopen
       
# class update_Parser(HTMLParser):
#     def __init__(self):
#         super().__init__()
#         self.date = []
#         self.in_tag_container = False

#     def handle_starttag(self, tag, attrs):
#         if tag == 'span':# and any(name == 'class' and value == 'sc-hLzWsc fWyBop' for name, value in attrs):
#             print(attrs)
#             self.in_tag_container = True
#             #date = (value for name, value in attrs if name == 'title')
#             #self.date.append(date.strip())
#             #self.date.append(datetime.strptime(date, '%a %b %d %Y %H:%M:%S GMT%z (%Z)'))# Adjust the date format
#             #self.in_tag_container = True

#     def handle_endtag(self, tag):
#         if tag == 'span' and self.in_tag_container:
#             self.in_tag_container = False

#     def handle_data(self, data):
#         if self.in_tag_container:
#             self.date.append(data.strip())

class update_Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.date = []
        self.in_tag_container = False

    def handle_starttag(self, tag, attrs):
        if tag == 'span':
            for name, value in attrs:
                if name == 'class' and value == 'sc-hLzWsc fWyBop':
                    self.in_tag_container = True
                elif name == 'title' and self.in_tag_container:
                    self.date.append(value)

    def handle_endtag(self, tag):
        if tag == 'span' and self.in_tag_container:
            self.in_tag_container = False

    def handle_data(self, data):
        if self.in_tag_container:
            #self.date.append(data.strip())
            pass




#my selector:
# site-content > div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > span > span:nth-child(2) > span



# Second trial

# Function to get the last update date from the webpage

def get_last_update_date(url):
    try:
        req = Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        response = urlopen(req)  # Open the URL
        if response.status == 200:
            page_content = response.read().decode('utf-8')
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find the span tag with the specific class
            selector = ('div.sc-dQelHR.iMCzUG > div > div.sc-cArzPw.ieazTD > div.sc-bSgIji.ciTtSM > span > span:nth-child(2) > span')

            date_element = soup.find(selector, class_='sc-hLzWsc fWyBop')
            print(date_element)
            if date_element:
                # Extract the date from the title attribute
                date_str = date_element.get[0]('title')
                print(date_str)
                return date_str
            else:
                print('No matching elements found on the webpage.')
        else:
            print('Failed to retrieve the webpage:', response.status)
    except Exception as e:
        print('Error:', e)
    return None


def scrap_page(page_content):
    print(page_content)
    parser = update_Parser()
    parser.feed(page_content)
    return parser.date

def main():
    try:
        # URL of the webpage with the dataset
        url = 'https://www.kaggle.com/datasets/hugovallejo/agroclimatology-data-of-the-state-of-paran-br/data'

        # Directory to save the dataset
        dataset_dir = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output'
        dataset_file = os.path.join(dataset_dir, 'agroclimatology.csv')
        #dataset_file2 = os.path.join(dataset_dir, 'produtividade_soja.csv')
     

        # Check if the dataset directory exists, if not, create it
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)
        
        req = Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        #open the page
        f = urlopen(req)
        page_content = f.read().decode('utf-8')

        # Load the last checked update date or set it to a very old date if it's the first run
        last_checked_date = datetime(2000, 1, 1)

        # Get the last update date from the webpage
        # update_date = get_last_update_date(url)
        update_date = scrap_page(page_content)
        print('C\'è qualcosa?', update_date)

    except Exception as e:
        print('Error:', e)
    return None



if __name__ == "__main__":
    main()









# # Function to download the updated dataset
# def download_dataset():
#     dataset_url = 'https://example.com/dataset/dataset.csv'  # Replace with the actual dataset URL
#     response = requests.get(dataset_url)
#     if response.status_code == 200:
#         with open(dataset_file, 'wb') as file:
#             file.write(response.content)
#         print('Dataset downloaded successfully.')
#     else:
#         print('Failed to download the dataset:', response.status_code)

# # Load the last checked update date or set it to a very old date if it's the first run
# last_checked_date = datetime(2000, 1, 1)

# # Get the last update date from the webpage
# update_date = get_last_update_date()
# print(update_date)

# # Compare the last checked date with the update date
# # if update_date and update_date > last_checked_date:
# #     print('Dataset is updated. Downloading the new version.')
# #     download_dataset()
# #     # Update the last checked date
# #     last_checked_date = update_date
# # else:
# #     print('Dataset is not updated. No need to download.')

# # You can save last_checked_date in a file or database for future runs


