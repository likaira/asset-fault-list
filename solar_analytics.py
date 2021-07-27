# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a Solar Analytics Webscrapper script file
This script utilises Selenium to read the SolarAnalytics site status page

Changelog
v1 : Initial version
v2: Updated to run on Raspberry Pi in headless mode

Created on Feb 25 2020
@author: Li.Kaira
"""
from run_browser import open_browser
from login_to_portal import login_to_solar_analytics
from save_to_csv import save_pd_data_frame_to_csv
from bs4 import BeautifulSoup
import pandas as pd
import datetime, time
import os, sys
from pathlib import Path

#print welcome statement
print("**  Running the Solar Analytics AFL Bot script...                       **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
username = os.environ.get('SA_USERNAME')
password = os.environ.get('SA_PASSWORD')

#use Selenium to open Solar Analytics and login
print("**  Opening Solar Analytics...                                          **")
browser = open_browser("https://my.solaranalytics.com/au/fleet/sites_list/?sorting=status")
login_to_solar_analytics(browser=browser, username=username, password=password)

#download site html source and extract table data    
try:
    result = browser.page_source
    soup = BeautifulSoup(result, 'lxml')
    table = soup.find_all('table')   
    print("**Data extraction from Solar Analytics successful. Browser will shutdown**")
    print(" ")
    browser.close()
except:
    print("**  Error: Page load unsuccessful. Program will shutdown                       **")
    browser.close()
    sys.exit(0)

#import site data from html code
data = (table[0]).find_all('td')
All_sites = [data[0:8],data[9:17],data[18:26],data[27:35]]
Site_names = []
Site_statuses = []
for site in All_sites:
    site_name = site[0].text
    site_status = site[7].text
    Site_names.append(site_name)
    Site_statuses.append(site_status)
    
#save site data as a pandas dataframe
sites = [Site_names, Site_statuses]
SolarAnaltyicsdf = pd.DataFrame(sites)
SolarAnaltyicsdf.rename ({0:'Site', 1:'Status'}, axis =1, inplace=True)

#save processed data to csv file 
save_pd_data_frame_to_csv(pd_data_frame=SolarAnaltyicsdf, name_append='_Fronius-InverterCounter')

#exit program
print("**  Solar Analytics AFL Bot script completed successfully.              **")
print("**                                                                      **")
print("**************************************************************************")
sys.exit(0)