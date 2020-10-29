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

def generate_URLs(county_codes=range(1, 59), city_codes=range(59, 507), county_level=False):
	"""Generate all possible county / city combinations
	If county_level true, only query for total county waste generation
	"""
	DATA_PATH = "https://www2.calrecycle.ca.gov/WasteCharacterization/ResidentialStreams?cy={}&lg={}&mt=0&bg=0&mtf=0"

	possible_URLs = []
	for county in county_codes:
	    if county_level:
	        possible_URLs.append(DATA_PATH.format(county, county+1000))
	    else:
	        for city in city_codes:
	            possible_URLs.append(DATA_PATH.format(county, city))
	return possible_URLs

def get_data(URL, download_path):
    """Exports excel file for a given county and city
    """
    driver.get(URL)
    wait = WebDriverWait(driver, 1.5)
    # NEED TO USE SINGLE QUOTES FOR CSS SELECTOR?
    jurisdiction_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#LocalGovernmentIDList_taglist > li > span:nth-child(1)')))
    county_element = driver.find_element_by_css_selector('#CountyID > option[selected="selected"]')

    county, jusrisdiction = county_element.text, jurisdiction_element.text

    driver.find_element_by_css_selector('#ExportToExcel').send_keys("\n")
    most_recent_waste_data = download_path + "/ResidentialStreamsExport.xlsx"
    print("Downloading data for county: {}, jurisdiction: {}".format(county, jusrisdiction))
    seconds_waited = 0
    while not os.path.exists(most_recent_waste_data):
#         print("Download taking {} seconds...".format(seconds_waited))
        time.sleep(1)
        seconds_waited += 1
    
    print("Download took {} seconds...".format(seconds_waited))
    new_file_name = download_path + "/" + county + "_" + jusrisdiction + ".xlsx"
    
    if os.path.isfile(most_recent_waste_data):
        os.rename(most_recent_waste_data, new_file_name)
        try:
            os.remove(most_recent_waste_data)
        except:
            pass
    
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

	# subset_county_codes = range(19, 20)
	# subset_city_codes = range(59, 63)
	# possible_URLs = generate_URLs(subset_county_codes)
	possible_URLs = generate_URLs(county_level=True)

	for url in tqdm(possible_URLs):
	    try:
	        driver = webdriver.Chrome(options=options)
	        get_data(url, PATH_TO_DOWNLOADS)
	        driver.quit()
	    except TimeoutException as exception:
	        # print("No data for this URL: ", url)
	        driver.quit()


