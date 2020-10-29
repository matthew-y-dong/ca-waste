import os
import time
import pandas as pd
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

PATH_TO_DOWNLOADS = "/Users/mdong/dataScience/projects-ml/waste-management/calrecycle-data"
options = Options()
prefs = {'download.default_directory' : PATH_TO_DOWNLOADS}
options.add_experimental_option('prefs', prefs)
options.headless = True

def generate_URLs(county_codes=range(1, 59), city_codes=range(59, 507)):
    """Generate all possible county / city combinations
    """
    DATA_PATH = "https://www2.calrecycle.ca.gov/WasteCharacterization/ResidentialStreams?cy={}&lg={}&mt=0&bg=0&mtf=0"
    possible_URLs = []
    for county in county_codes:
        for city in city_codes:
            possible_URLs.append(DATA_PATH.format(county, city))

    return possible_URLs

def get_data(URL, download_path):
    """Exports excel file for a given county and city
    """
    driver.get(URL)
    wait = WebDriverWait(driver, 1.5)
    # NEED TO USE SINGLE QUOTES FOR CSS SELECTOR
    city_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#LocalGovernmentIDList_taglist > li > span:nth-child(1)')))
    county_element = driver.find_element_by_css_selector('#CountyID > option:nth-child(2)')
    
    driver.find_element_by_css_selector('#ExportToExcel').send_keys("\n")
    most_recent_waste_data = download_path + "/ResidentialStreamsExport.xlsx"
    print("Downloading data for county: {}, city: {}".format(county_element.text, city_element.text))
    seconds_waited = 0
    while not os.path.exists(most_recent_waste_data):
        print("Download taking {} seconds...".format(seconds_waited))
        time.sleep(1)
        seconds_waited += 1
        
    new_file_name = download_path + "/" + county_element.text + "_" + city_element.text + ".xlsx"
    
    if os.path.isfile(most_recent_waste_data):
        os.rename(most_recent_waste_data, new_file_name)
    
    convert_to_csv(new_file_name)

def convert_to_csv(path):
    """Convert the Excel file into a csv with the same name given path to the file
    """
    directory = os.path.dirname(path)
    file_name_w_ext = os.path.basename(path)
    file_name = os.path.splitext(file_name_w_ext)[0]
    csv_file_path = os.path.join(directory, file_name + ".csv")
    
    data_xls = pd.read_excel(path, 'Data-Residential Composition')
    data_xls.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
	possible_URLs = generate_URLs()

	for url in tqdm(possible_URLs):
	    try:
	        driver = webdriver.Chrome(options=options)
	        get_data(url, PATH_TO_DOWNLOADS)
	    except TimeoutException as exception:
	        # print("No data for this URL: ", url)
	        driver.quit()
	driver.quit()


