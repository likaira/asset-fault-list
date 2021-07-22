# -*- coding: utf-8 -*-
"""
Spyder Editor

This is an SMA ennexOS Webscrapper script file

Created on Thu NOv 28 12:08:12 2019

@author: Li.Kaira

v2- Updated input csv file to indicate Project Group for Hillsong site(s)
v3 - Updated BOM ID's to be 6 characters long and used Selenium to extract BOM data
v4 - Updated to run on Raspeberry Pi in headless mode
"""
#import packages
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests as rq
from pathlib import Path
import time
import datetime
from progress.bar import Bar
from run_browser import open_browser
from bom_reader import get_bom_data
from save_to_csv import save_pd_data_frame_to_csv

#define urls
init_url = "https://ennexos.sunnyportal.com/dashboard"
base_url = "https://ennexos.sunnyportal.com/"
end_url = "/monitoring/view-status-list"

#print welcome statement
print("**  Running the SMA ennexOS AFL Bot script...                           **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
username = os.environ.get('ENNEX_USERNAME')
password = os.environ.get('ENNEX_PASSWORD')

#function definitions
#define a function to login to EnnexOS
def login_to_portal(browser, username, password):
    browser.find_element_by_name("username").send_keys(username)
    browser.find_element_by_name("password").send_keys(password)
    time.sleep(3)
    browser.find_element_by_tag_name("button").click()

#import site data from csv file 'ennex.csv'
ennexList = pd.read_csv('Inputs/test_ennex.csv', header=0)

#Open ennexOS Page
print("**  Opening SMA EnnexOS Portal...                                        **")
try:
    browser = open_browser(init_url)   
except:
    print("**  Error: Page load unsuccessful. Program will shutdown                       **")
    browser.close()

#Login to ennexOS    
print("**  Logging in to SMA ennexOS...                                      **")
try:
    login_to_portal(browser=browser, username=username, password=password)
except:
    print("**  Error: Login unsuccessful. Program will shutdown                       **")
    browser.close()

#add unique siteId url to siteId dataframe
ennexList['ennex-Id']=ennexList['ennex-Id'].apply(lambda x: '{0:0>6}'.format(x))
ennexList['ennex-url'] = base_url + ennexList['ennex-Id'] + end_url

#download generation data for each site
print("**  Downloading generation data from ennexOS                            **")
actual_kWh = []
for url in ennexList['ennex-url']:
    try:        
        #download site html source and extract table
        time.sleep(10)
        result = browser.page_source
        soup = BeautifulSoup(result, 'lxml')
        table = soup.find_all('table')
        data = pd.read_html(str(table))
        ennexdf = data[0]        
        #get previous day generation values in [kWh]
        generation = ennexdf.iloc[:,-5]
        generation = pd.to_numeric(generation, errors='coerce')
        generation.fillna(0)
        total = generation.sum()
        actual_kWh.append(total)
    
    except:
        #download site html source and extract table
        time.sleep(10)
        result = browser.page_source
        soup = BeautifulSoup(result, 'lxml')
        table = soup.find_all('table')
        data = pd.read_html(str(table))
        ennexdf = data[0]
        #get previous day generation values in [kWh]
        generation = ennexdf.iloc[:,-5]
        generation = pd.to_numeric(generation, errors='coerce')
        generation.fillna(0)
        total = generation.sum()
        actual_kWh.append(total)
    
print("**  Generation data download successful                                 **")  
browser.close()  


#Get weather data from BOM
link_to_stationIds = "Inputs/test_ennex_bom_urls.csv"
bom_data = get_bom_data(link_to_stationIds)   
ennexList['irrad_yday'] = bom_data

print("**  Weather data download successful                                    **")

#drop url column
drop_cols = ['ennex-url']
ennexList.drop(drop_cols, axis = 1, inplace=True)

#calculate expected PV generation for yesterday
#kWh/m^2 * m^2/kW * kW * efficiency
#assumed 6.5 for m^2/kW and 0.15 for efficiency
ennexList['actual-kWh'] = actual_kWh
ennexList['expected-kWh'] = ennexList['irrad_yday'] * 6.5 * ennexList['PV_System_Power'] * 0.15

#calculate generation ratio and sort table by Generation Ratio Ascending
ennexList['Generation_Ratio'] = ennexList['actual-kWh'].divide(ennexList['expected-kWh'], fill_value=0)
ennexList.sort_values(by=['Generation_Ratio'], inplace=True)

#output site list with generation values less 75% of expected values
SMAlowGen = ennexList.loc[ennexList['Generation_Ratio'] < 0.75].copy()
SMAlowGen.sort_values(by=['Generation_Ratio'], inplace=True)
save_pd_data_frame_to_csv(pd_data_frame=SMAlowGen, name_append='Ennex_Low_Production_Sites')
save_pd_data_frame_to_csv(pd_data_frame=ennexList, name_append='Ennex_All_Sites')

#exit program
print("**  SMA ennexOS AFL Bot script completed successfully.                  **")
print("**                                                                      **")
print("**************************************************************************")
exit
