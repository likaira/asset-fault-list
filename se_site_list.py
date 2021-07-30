# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a Solaredge API script file to return the list of sites associated with the Verdia account
API Documentation: https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf

Changelog
v1 : Initial version
v2: Updated to run on Raspberry Pi in headless mode
"""
import requests as rq
import json as js
import pandas as pd
from save_to_csv import save_pd_data_frame_to_csv
import os

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
API_KEY = os.environ.get('SE_API_KEY')


#print program introduction
print("This program returns the list of SolarEdge sites associated with the Verdia account")

#SITE LIST

#build url for sites 1 -100
#-------------------------------------------------
url1 = "https://monitoringapi.solaredge.com/sites/list?&size=100&startIndex="
url2 = '0'
url3 = "&api_key="
url = url1 + url2 + url3 + API_KEY
#-------------------------------------------------

response = rq.get(url)
#Check if valid response is received and print output
if response.status_code == 200:
    print("API 1 successful")
    parsed = js.loads(response.content)         
    list_A = pd.json_normalize(parsed, record_path=['sites', 'site'])      #extract site data from json
        
else:
    print("Error running API - please check API documentation for changes")

#build url for sites 100+
#-------------------------------------------------
url2 = '100'
url = url1 + url2 + url3 + API_KEY
#-------------------------------------------------
#
response = rq.get(url)
#Check if valid response is received and print output
if response.status_code == 200:
    print("API 2 successful")
    parsed = js.loads(response.content)         
    list_B = pd.json_normalize(parsed, record_path=['sites', 'site'])      #extract site data from json
        
else:
    print("Error running API - please check API documentation for changes")


#----------------------------------------------
#JOIN SITE LIST AND SAVE AS Excel file
site_list_data_frame = pd.concat([list_A,list_B], ignore_index=True,sort=True)

#save processed data to csv file 
save_pd_data_frame_to_csv(pd_data_frame=site_list_data_frame, name_append='_SE_SiteList')

#exit program
print("**  Solar Edge Site List API call run successfully.                     **")
print("**                                                                      **")
print("**************************************************************************")
exit