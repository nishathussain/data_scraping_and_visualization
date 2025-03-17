## Added Functionality (run python download_EIAdnav_data.py)
import os, re, requests
from lxml import html
from urllib.parse import urljoin

INPUT_URLs = ["https://www.eia.gov/dnav/pet/pet_pnp_inpt_dc_nus_mbbl_m.htm",
            "https://www.eia.gov/dnav/pet/pet_pnp_wiup_dcu_nus_w.htm"]
BASE_DIR  = "NetInput_RefineryBlender" # Directory to store downloaded files

def get_excel_links(url=None):
    """Scrape and return links of all Excel files"""
    response = requests.get(url)
    if not response.status_code == 200: # Error handling
        print("Failed to retrieve the page")
        return None
    tree = html.fromstring(response.content)
    excel_links = tree.xpath("//a[contains(@href, '.xls')]/@href") # get xls & xlsx
    excel_links = list(set(excel_links))
    excel_links = [os.path.join(os.path.dirname(url),link) for link in excel_links]
    return excel_links
def save_excel_files(links=None, BASE_DIR=None):
    """Download and save files"""
    for link in links:
        file_path = os.path.join(os.path.curdir, BASE_DIR, os.path.basename(link))
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
    for inputs in INPUT_URLs:
        excel_links = get_excel_links(url=inputs) # get all xls/xlsx links
        if excel_links:
            save_excel_files(links=excel_links,BASE_DIR=BASE_DIR)
        else:
            print("No Excel file found.")