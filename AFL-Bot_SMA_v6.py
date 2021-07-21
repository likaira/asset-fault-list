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
import requests as rq
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import datetime, time
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

#use Selenium to open Sunny Portal and extract PV data
print("**  Opening SMA Sunny Portal...                                         **")
try:
    try:            #try Firefox browser, in headless mode
        # driver = 'Driver/geckodriver.exe'        
        # options = Options()
        # options.headless = True
        # browser = webdriver.Firefox(executable_path=driver, options=options)  
        # display = Display(visible=0, size=(800, 600))  
        # display.start()
        driver = webdriver.Firefox
        options = Options()
        options.headless = True
        browser = webdriver.Firefox(executable_path=driver, options=options)  
    except:         #try Chrome browser      
        driver = 'Driver/chromedriver.exe'        
        browser = webdriver.chrome(executable_path=driver)
    #open SMA Sunny Portal and login
    browser.get("https://www.sunnyportal.com/Plants")
    time.sleep(5)                   #wait for page to load
    try:        #Accept Cookies
        browser.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
        time.sleep(1)
    except:
        print("**  Error: Page load unsuccessful. Program will shutdown                       **")
        browser.close()
        exit    
    browser.find_element_by_id("txtUserName").send_keys(username)
    browser.find_element_by_id("txtPassword").send_keys(password)
    browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_Logincontrol1_MemorizePassword"]').click()
    time.sleep(2)
    browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_Logincontrol1_LoginBtn"]').click()
    
    #sort Table by PV System column
    print("**  Downloading Generation Data from SMA Sunny Portal...                          **")
    try:
        timeout = 30 
        WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))                  #wait for page to load            
    except TimeoutException:
        print("**  Error: Page load unsuccessful. Program will shutdown                       **")
        browser.close()
        exit
    finally:
        browser.find_element_by_xpath('/html/body/div[4]/div/div/div[2]/table/thead/tr/th[1]/div').click()
    #download site html source and extract table
    time.sleep(5)                  #wait for page to load
    result = browser.page_source
    soup = BeautifulSoup(result, 'lxml')
    table = soup.find_all('table')
    data = pd.read_html(str(table))
    SMAdf = data[0]
    print("**Data extraction from SMA Sunny Portal successful.          **")
    print(" ")
    browser.close()
except:
    print("**  Error: Page load unsuccessful. Program will shutdown                       **")
    browser.close()
    exit

#import station Ids from external csv file and format to be 6 digits long
stationId = pd.read_csv("Inputs/BOM-url.csv", header=0)
stationId['Id']=stationId['Id'].apply(lambda x: '{0:0>6}'.format(x)) 

#add unique station url to stationId dataframe
base_url = "http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=193&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num="
stationId['url'] = base_url + stationId['Id']

#get day and month forr use in extracting yesterday's radiation data
today = datetime.date.today()
month = today.month
day=today.day

#initiliase counter
index = 0
irrad_yday = []

#Open bom.gov.au,extract values Solar exposure tables and save as a new colum in stationId dataframe
bar = Bar('Downloading data from BOM.gov.au', max = len(stationId['Id']))

for url in stationId['url']:
    driver = 'Driver/geckodriver.exe'        
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(executable_path=driver, options=options) 
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

stationId['irrad_yday'] = irrad_yday
bar.finish()
   
#drop unwanted columns from SMAdf: 4th Column and onwards 
length = len(SMAdf.columns)
drop_cols = list(range(3,length))
SMAdf.drop(SMAdf.columns[drop_cols], axis = 1, inplace=True)

#combine SMAdf and stationId dataframes to new dataframae: SMAsiteList
SMAsiteList = pd.merge(SMAdf, stationId, on='PV System')
unwantedColumns = [3,4]
SMAsiteList.drop(SMAsiteList.columns[unwantedColumns], axis = 1, inplace=True)
SMAsiteList.iloc[:,2] = pd.to_numeric(SMAsiteList.iloc[:,2], errors='coerce')  #convert SMA generation data to numeric values
actual_kWh = SMAsiteList.columns[2]

#calculate expected PV generation for yesterday
#kWh/m^2 * m^2/kW * kW * efficiency
#assumed 6.5 for m^2/kW and 0.15 for efficiency
SMAsiteList['expected_kWh'] = SMAsiteList['irrad_yday'] * 6.5 * SMAsiteList['PV system power[kW]'] * 0.15

#calculate ratio of actual generation to expected generation
SMAsiteList['Generation_Ratio'] = SMAsiteList[actual_kWh]/SMAsiteList['expected_kWh']
SMAsiteList['Generation_Ratio'].fillna(0, inplace=True)

#output site list with generation values less 75% of expected values
SMAlowGen = SMAsiteList.loc[SMAsiteList['Generation_Ratio'] < 0.75].copy()
SMAlowGen.sort_values(by=['Generation_Ratio'], inplace=True)
#print("Sites with actual generation values less than 75% of expected values: ")

todayString = datetime.datetime.now().strftime("%Y%m%d")

#get current date and time to use in output file name
timeString = datetime.datetime.now().strftime("%Y%m%d-%H%M")

#save processed data to excel file
folderSave = Path("OutputFiles")
saveName = timeString + '_SMA-Output'
saveLocation = folderSave/saveName
saveLocation = saveLocation.with_suffix(saveLocation.suffix + '.xlsx')

writer =  pd.ExcelWriter(saveLocation, engine='xlsxwriter')
SMAlowGen.to_excel(writer, sheet_name="Underperforming Sites")
SMAsiteList.to_excel(writer, sheet_name="All Sites")
writer.save()

#open excel file
os.startfile(saveLocation)

#exit program
print("**  SMA Sunny Portal AFL Bot script completed successfully.             **")
print("**                                                                      **")
print("**************************************************************************")
exit

