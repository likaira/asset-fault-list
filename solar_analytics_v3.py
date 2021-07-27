# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a Solar Analytics Webscrapper script file
This script utilises Selenium to read the SolarAnalytics site status page

Changelog
v1 : Initial version
v2: Updated to run on Raspberry Pi in headless mode
v3: Updated to use the Solar AnalyticsAPI 

Created on Feb 25 2020
@author: Li.Kaira
"""
import requests as rq
import json as js
import os
import pandas as pd
from save_to_csv import save_pd_data_frame_to_csv

#print welcome statement
print("**  Running the Solar Analytics AFL Bot script...                       **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
username = os.environ.get('SA_USERNAME')
password = os.environ.get('SA_PASSWORD')

#build url
url1 = "https://portal.solaranalytics.com.au"
url2 = "/api/v3/site_list"
url = url1 + url2 

#get site information for all sites
response = rq.get(url, auth=(username, password))
#Check if valid response is received and extract data
if response.status_code == 200:
    parsed = js.loads(response.content)   
    SolarAnalyticsdf = pd.json_normalize(parsed, record_path=['data']) 
    print(SolarAnalyticsdf)
    
else:
    print("Error running API - please check API documentation for any changes")

#save processed data to csv file 
save_pd_data_frame_to_csv(pd_data_frame=SolarAnalyticsdf, name_append='_SolarAnalytics_Status')

#exit program
print("**  Solar Analytics AFL Bot script completed successfully.              **")
print("**                                                                      **")
print("**************************************************************************")
exit