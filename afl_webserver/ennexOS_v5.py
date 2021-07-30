# -*- coding: utf-8 -*-
"""
Spyder Editor

This is an SMA ennexOS Webscrapper script file

Created on Thu NOv 28 12:08:12 2019

@author: Li.Kaira

v2- Updated input csv file to indicate Project Group for Hillsong site(s)
v3 - Updated BOM ID's to be 6 characters long and used Selenium to extract BOM data
v4 - Updated to run on Raspeberry Pi in headless mode
v5 - Integrated with Django webserver 
"""
#Setup Python Script to use the Django ORM
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afl_webserver.settings")
django.setup()

#Import packages for script
from main.models import PVSystem, ErrorLog
import pandas as pd
from progress.bar import Bar
from download_ennex_generation_data import download_data
from bom_reader import get_bom_data


#define urls
init_url = "https://ennexos.sunnyportal.com/dashboard"
base_url = "https://ennexos.sunnyportal.com/"
end_url = "/monitoring/view-status-list"

#print welcome statement
print("**  Running the SMA ennexOS AFL Bot script...                           **")

#Change working directory to directory of script file
# directory = os.path.dirname(os.path.realpath(__file__))
# os.chdir(directory)

#read login credentials from Environment variables
username = os.environ.get('ENNEX_USERNAME')
password = os.environ.get('ENNEX_PASSWORD')

#import site data from csv file 'ennex.csv'
ennexList = pd.read_csv('../Inputs/test_ennex.csv', header=0)

#add unique siteId url to siteId dataframe
ennexList['ennex-Id']=ennexList['ennex-Id'].apply(lambda x: '{0:0>6}'.format(x))
ennexList['ennex-url'] = base_url + ennexList['ennex-Id'] + end_url

#Download generation data for each site
bar = Bar('Downloading generation data from ennexOS', max = len(ennexList['ennex-url']))
actual_kWh = []
for url in ennexList['ennex-url']:
    total = download_data(url=url, username=username, password=password)
    actual_kWh.append(total)
    bar.next()

bar.finish()
print("**  Generation data download successful                                 **")  


#Download weather data from BOM
link_to_stationIds = "../Inputs/test_ennex_bom_urls.csv"
bom_data = get_bom_data(link_to_stationIds)   
# ennexList['irrad_yday'] = bom_data

print("**  Weather data download successful                                    **")

#combine ennexList and bom_data dataframes 
ennexList = pd.merge(ennexList, bom_data, on='PV_System')

#drop unwanted columns
drop_cols = ['ennex-url', 'Id', 'url', 'ennex-Id', 'bom-Id']
ennexList.drop(drop_cols, axis = 1, inplace=True)


#calculate expected PV generation for yesterday
#kWh/m^2 * m^2/kW * kW * efficiency
#assumed 6.5 for m^2/kW and 0.15 for efficiency
ennexList['actual_kWh'] = actual_kWh
ennexList['expected_kWh'] = ennexList['irrad_yday'] * 6.5 * ennexList['PV_System_Power'] * 0.15

#calculate generation ratio and sort table by Generation Ratio Ascending
ennexList['Generation_Ratio'] = ennexList['actual_kWh'].divide(ennexList['expected_kWh'], fill_value=0)
ennexList.sort_values(by=['Generation_Ratio'], inplace=True)

#output site list with generation values less 75% of expected values
ennexLowGen = ennexList.loc[ennexList['Generation_Ratio'] < 0.75].copy()
ennexLowGen.sort_values(by=['Generation_Ratio'], inplace=True)

print(ennexLowGen)

# save_pd_data_frame_to_csv(pd_data_frame=ennexLowGen, name_append='Ennex_Low_Production_Sites')
# save_pd_data_frame_to_csv(pd_data_frame=ennexList, name_append='Ennex_All_Sites')

#create list of objects to upload to Database, model - ErrorLog
iterate_rows = ennexLowGen.iterrows()
objs = [
    ErrorLog(
        pvsystem = PVSystem.objects.get(name=row['name']),
        fault_type = 'System under-performance',
        description = f"System generation {row['actual_kWh']} kWh versus expected generation of {row['expected_kWh']} kWh",                  
    )
    for index, row in iterate_rows
]

#Bulk create Error Logs
ErrorLog.objects.bulk_create(objs)
print("Batch upload complete")

#exit program
print("**  SMA ennexOS AFL Bot script completed successfully.                  **")
print("**                                                                      **")
print("**************************************************************************")
exit
