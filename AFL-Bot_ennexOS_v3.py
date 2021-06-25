# -*- coding: utf-8 -*-
"""
Spyder Editor

This is an SMA ennexOS Webscrapper script file

Created on Thu NOv 28 12:08:12 2019

@author: Li.Kaira

v2- Updated input csv file to indicate Project Group for Hillsong site(s)
v3 - Updated BOM ID's to be 6 characters long and used Selenium to extract BOM data
"""
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests as rq
from pathlib import Path
import time
import datetime
from progress.bar import Bar

#print welcome statement
print("**  Running the SMA ennexOS AFL Bot script...                           **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from text file
credentials = open('Credentials/credentials.txt', "r")
lines = credentials.readlines()
username = lines[0]
password = lines[1]
credentials.close()

#get day and month
today = datetime.date.today()
month = today.month
day=today.day
todayString = datetime.date.today().strftime("%Y%m%d")

#import site data from csv file 'ennex.csv'
ennexList = pd.read_csv('Inputs/ennex.csv', header=0)

#add unique station url to stationId dataframe
base_url = "http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=193&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num="
ennexList['bom-Id']=ennexList['bom-Id'].apply(lambda x: '{0:0>6}'.format(x))        #make all ids 6 characters long
ennexList['bom-url'] = base_url + ennexList['bom-Id']

#initiliase variables
index = 0
irrad_yday = []
actual_kWh = []


#use Selenium to open BOM web and get weather data
bar = Bar('Downloading data from BOM.gov.au', max = len(ennexList['bom-Id']))

for url in ennexList['bom-url']:
    driver = 'Driver/geckodriver.exe'
    browser = webdriver.Firefox(executable_path=driver)
    try:
        browser.get(url)
        time.sleep(10)
        BOMdata = browser.page_source
        soup = BeautifulSoup(BOMdata, 'lxml')    
        BOMtable = soup.find_all('table')[0]
        BOMdf = pd.read_html(str(BOMtable))[0]
        irrad_value = BOMdf.iat[day-1,month]/3.6                    
        #irrad_value = BOMdf.iat[30,9]
        irrad_yday.append(irrad_value) 
    except:
        print("**  Error: Page load unsuccessful.                        **")
        irrad_value = 0 
        irrad_yday.append(irrad_value) 
    browser.close()
    index = index + 1
    bar.next()
 
    
ennexList['irrad_yday'] = irrad_yday
bar.finish()
print("**  Weather data download successful                                    **")

#add unique siteId url to siteId dataframe
init_url = "https://ennexos.sunnyportal.com/dashboard"
base_url = "https://ennexos.sunnyportal.com/"
end_url = "/monitoring/view-status-list"
ennexList['ennex-Id']=ennexList['ennex-Id'].apply(lambda x: '{0:0>6}'.format(x))
ennexList['ennex-url'] = base_url + ennexList['ennex-Id'] + end_url

#use Selenium to open ennexOS webpage and login
driver = 'Driver/geckodriver.exe'
browser = webdriver.Firefox(executable_path=driver)
browser.get(init_url)
time.sleep(5)
browser.find_element_by_name("username").send_keys(username)
browser.find_element_by_name("password").send_keys(password)
time.sleep(3)
browser.find_element_by_tag_name("button").click()
time.sleep(10)

#download generation data for each site
print("**  Downloading generation data from ennexOS                            **")
for url in ennexList['ennex-url']:
    try:
        #open website and login
        browser.get(url)
        browser.find_element_by_tag_name("button").click()
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

#drop url columns
drop_cols = ['bom-url' , 'ennex-url']
ennexList.drop(drop_cols, axis = 1, inplace=True)

#calculate expected PV generation for yesterday
#kWh/m^2 * m^2/kW * kW * efficiency
#assumed 6.5 for m^2/kW and 0.15 for efficiency
ennexList['actual-kWh'] = actual_kWh
ennexList['expected-kWh'] = ennexList['irrad_yday'] * 6.5 * ennexList['PV_System_Power'] * 0.15

#calculate generation ratio and sort table by Generation Ratio Ascending
ennexList['Generation_Ratio'] = ennexList['actual-kWh'].divide(ennexList['expected-kWh'], fill_value=0)
ennexList.sort_values(by=['Generation_Ratio'], inplace=True)

#get current date and time to use in output file name
timeString = datetime.datetime.now().strftime("%Y%m%d-%H%M")

#save processed data to excel file
folderSave = Path("OutputFiles")
saveName = timeString + '_ennex-Output'
saveLocation = folderSave/saveName
saveLocation = saveLocation.with_suffix(saveLocation.suffix + '.xlsx')

writer =  pd.ExcelWriter(saveLocation, engine='xlsxwriter')
ennexList.to_excel(writer, sheet_name="ennexOs Analysis")
writer.save()

#open excel file
os.startfile(saveLocation)

#exit program
print("**  SMA ennexOS AFL Bot script completed successfully.                  **")
print("**                                                                      **")
print("**************************************************************************")
exit
