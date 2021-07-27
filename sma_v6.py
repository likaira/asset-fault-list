# -*- coding: utf-8 -*-
"""
Spyder Editor

This is an SMA Webscrapper script file
This script utilises Selenium to download SMA generation data without user input

Changelog
v1 to v2 : Removed requirement for user to manually download csv file from Sunny Portal.
            Script now runs Selenium to scrap data from Sunny Portal html page.
v2 to v3 : Reduced threshold for under-performance from 80% to 75%
v4: Implemented Selenium Built in WebDriver wait tool to wait for page to load.
v5: Updated BOM ID's to be 6 characters long and used Selenium to extract BOM data
v6: Updated to run in headless mode. Accept Cookies on the SMA home page.

Created on Wed Dec 18 2019
@author: Li.Kaira
"""

#import packages
import requests as rq
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from run_browser import open_browser
from bom_reader import get_bom_data
from save_to_csv import save_pd_data_frame_to_csv
from login_to_portal import login_to_sma
import pandas as pd
import time
import os
from pathlib import Path
from progress.bar import Bar

#print welcome statement
print("**  Running the SMA Sunny Portal AFL Bot script...                      **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
username = os.environ.get('SUNNY_USERNAME')
password = os.environ.get('SUNNY_PASSWORD')

#function definitions

#Open Sunny Portal Page
print("**  Opening SMA Sunny Portal...                                         **")
try:
    browser = open_browser("https://www.sunnyportal.com/Plants")   
    try:        #Accept Cookies (if Cookies banner exists)
        browser.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
        time.sleep(1)
    except:
        pass        
except:         #fail safe execution   
    print("**  Error: Page load unsuccessful. Program will shutdown                       **")
    exit

#Login to Sunny Portal    
print("**  Logging in to SMA Sunny Portal...                                      **")
try:
    login_to_sma(browser=browser, username=username, password=password)
except:
    print("**  Error: Login unsuccessful. Program will shutdown                       **")
    browser.close()

#Extract PV system data from SMA Portal    
   
#sort Table by PV System column
print("**  Downloading Generation Data from SMA Sunny Portal...                        **")
try:
    timeout = 30 
    WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))                  #wait for page to load            
except TimeoutException:
    print("**  Error: Page load unsuccessful. Program will shutdown                       **")
    browser.close()    
finally:
    browser.find_element_by_xpath('/html/body/div[4]/div/div/div[2]/table/thead/tr/th[1]/div').click()

#download site html source and extract table
time.sleep(5)                  #wait for page to load
try:
    result = browser.page_source
    soup = BeautifulSoup(result, 'lxml')
    table = soup.find_all('table')
    data = pd.read_html(str(table))
    SMAdf = data[0]
    print("**Data extraction from SMA Sunny Portal successful.                  **")    
    print(" ")
    browser.close()
except:
    print("**  Error: Page load unsuccessful. Program will shutdown                       **")
    browser.close()

#Get weather data from BOM
link_to_stationIds = "Inputs/sunny_portal_bom_urls.csv"
bom_data = get_bom_data(link_to_stationIds)
   
#drop unwanted columns from SMAdf: 4th Column and onwards 
length = len(SMAdf.columns)
drop_cols = list(range(3,length))
SMAdf.drop(SMAdf.columns[drop_cols], axis = 1, inplace=True)

#combine SMAdf and bom_data dataframes to new dataframe: SMAsiteList
SMAsiteList = pd.merge(SMAdf, bom_data, on='PV System')
unwantedColumns = [3,4]
SMAsiteList.drop(SMAsiteList.columns[unwantedColumns], axis = 1, inplace=True)
SMAsiteList.iloc[:,2] = pd.to_numeric(SMAsiteList.iloc[:,2], errors='coerce')  #convert SMA generation data to numeric values
actual_kWh = SMAsiteList.columns[2]

#calculate expected PV generation for previous day
#kWh/m^2 * m^2/kW * kW * efficiency
#assumed 6.5 for m^2/kW and 0.15 for efficiency
SMAsiteList['expected_kWh'] = SMAsiteList['irrad_yday'] * 6.5 * SMAsiteList['PV system power[kW]'] * 0.15

#calculate ratio of actual generation to expected generation
SMAsiteList['Generation_Ratio'] = SMAsiteList[actual_kWh]/SMAsiteList['expected_kWh']
SMAsiteList['Generation_Ratio'].fillna(0, inplace=True)

#output site list with generation values less 75% of expected values
SMAlowGen = SMAsiteList.loc[SMAsiteList['Generation_Ratio'] < 0.75].copy()
SMAlowGen.sort_values(by=['Generation_Ratio'], inplace=True)
save_pd_data_frame_to_csv(pd_data_frame=SMAlowGen, name_append='SMA_Low_Production_Sites')
save_pd_data_frame_to_csv(pd_data_frame=SMAsiteList, name_append='SMA_All_Sites')


print("**  SMA Sunny Portal AFL Bot script completed successfully.             **")
print("**                                                                      **")
print("**************************************************************************")
exit

