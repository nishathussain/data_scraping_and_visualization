## Added Functionality (python download_EIA_data.py)
#1. Years: A list of years to only download required data, years as None will download all year's data
#2. Redshift/Athena format directory structure of downloaded data 
#3. Error handling with verbiage to notify user in case of error

import os, re, requests
from lxml import html
from urllib.parse import urljoin

INPUT_URL = "https://www.eia.gov/outlooks/steo/outlook.php" # input URL to scrape
BASE_DIR  = "EIA_Excel_Files" # Directory to store downloaded files

def get_excel_links(url=INPUT_URL):
    """Scrape and return links of all Excel files"""
    response = requests.get(url)
    if not response.status_code == 200: # Error handling
        print("Failed to retrieve the page")
        return None
    tree = html.fromstring(response.content)
    excel_links = tree.xpath("//a[contains(@href, '_base.xls')]/@href") # get xls & xlsx
    excel_links = [os.path.dirname(INPUT_URL)+os.sep+ link for link in excel_links]
    return excel_links
def get_date(addr):
    """Get month and year"""
    pattern = r"/archives/([a-z]{3})(\d{2})_"
    match = re.search(pattern, addr.lower())
    if match:
        month = match.group(1); year='20'+match.group(2)
        return (month,year)
    else:
        return ('default','default') # regex error 
def save_excel_files(links=None, BASE_DIR=None, years=None):
    """Download and save files in year/month folder structure, years to download selected year only"""
    for link in links:
        month, year=get_date(link)
        if (years is not None) and year not in years: continue
        file_path = os.path.join(os.path.curdir, BASE_DIR, year, month, os.path.basename(link))
        os.makedirs(os.path.dirname(file_path), exist_ok=True) # directory structure
        print(f"Downloading: {link}")
        response = requests.get(link, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
        else:
            print(f"Failed to download: {filename}")
if __name__ == "__main__":
    print("Scraping url...")
    excel_links = get_excel_links() # get all xls/xlsx links
    if excel_links:
        print(f"Found: {len(excel_links)} Excel files.")
        save_excel_files(links=excel_links,BASE_DIR=BASE_DIR, years=['2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025'])
    else:
        print("No Excel file found.")
