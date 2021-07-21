# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a Fronius Webscrapper script file that opens the realtime inverter
power production pages on Solar.Web and counts the number of online inverters

This script uses the link on Fronius Solar Web to open each site
By replicating a mouse click - instead of pasting the site link on the url bar (v1)
The old method had a high number of false alerts due to some sites not availing data
This method is slower to run, but will minimise false alerts.

Created on Wed Dec 18 2019
@author: Li.Kaira

v3 - updated to manage cookies without user input
v4 - updated to match the new layout in the SolarWeb Analysis page
V5 - changed the data extraction provcessing when counting the number of online inverters
v6 - updated to run on Raspberry Pi
"""
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
from pathlib import Path
import time
import datetime


#print welcome statement
print("**  Running the Fronius Inverter Counter AFL Bot script...              **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
username = os.environ['FRONIUS_USERNAME']
password = os.environ['FRONIUS_PASSWORD']


#use Selenium to open Fronius and extract site ids
print("**  Opening Fronius Solar.Web...                                        **")
try:
    try:            #try Firefox browser
        driver = 'Driver/geckodriver.exe'
        browser = webdriver.Firefox(executable_path=driver)
    except:         #try Chrome browser        
        driver = 'Driver/chromedriver.exe'
        browser = webdriver.Chrome(executable_path=driver)
    #open Fronius Solar Web and login
    browser.get("https://www.solarweb.com/PvSystems/Widgets")
    time.sleep(3)
    
    #accept cookies
    try:
        browser.find_element_by_xpath("/html/body/header/div[1]/div/p[2]/button").click()
        time.sleep(3)
    except:
        pass
    
    #login
    browser.find_element_by_id("username").send_keys(username)
    browser.find_element_by_id("password").send_keys(password)
    time.sleep(3)
    browser.find_element_by_id("submitButton").click()
    time.sleep(10)
    
    #accept cookies
    try:
        #browser.current_window_handle(browser.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click())
        browser.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()
        time.sleep(3)
    except:
        time.sleep(3)
        pass

    #select 'Show All' in Fronius page, after waiting 15 seconds for page to load
    try:
        browser.find_element_by_xpath("//select[@name='js-pvsystem-table-id_length']/option[text()='All']").click()
    except:
        print("Error: Page load unsuccessful. Portal might be down, please try again later.")
        exit

    #download site html source and extract table
    time.sleep(2)
    result = browser.page_source
    soup = BeautifulSoup(result, 'lxml')
    table = soup.find_all('table')
    data = pd.read_html(str(table))
    Froniusdf = data[0]
except:
    print("Error: Page load unsuccessful. Program will shutdown")
    exit

#drop unwanted columns
dropCols = ['Unnamed: 0', 'kWh/kWp', 'kWh Today', 'Last update', 'Errors (today)']
Froniusdf.drop(dropCols, axis = 1, inplace=True)

#rename 'Inv.' column to 'Inverters_Installed'
Froniusdf = Froniusdf.rename(columns = {'Inv.' : 'Inverters_Installed'})

#iterate through all PV systems and extract number of inverters online
print("**  InverterCounter is running...                                       **")
print("**                                                                      **")
InverterCounter = []

for site in Froniusdf['PV system']:                 
    try:
        site = f'"{site}"'              #format site name to append inverted commas, allows for more specific searching on Fronius portal
        browser.find_element_by_id("pvsystem-search").send_keys(site)                #search for individual site
        time.sleep(2)                   #wait for page to load

        #open site page 
        try:
            browser.find_element_by_class_name("sorting_1").click()                     #click first result
            time.sleep(3)
            browser.find_element_by_css_selector('li.js-menu-item:nth-child(3) > a:nth-child(1) > span:nth-child(1)').click()   #click 'Analysis'
            time.sleep(5)
            #extract number of inverters producing power from POWER graph
            print("InverterCounter is extracting data from SOLAR.WEB...")
            inverter_data_extracted = []

            try:
                result = browser.page_source
                soup = BeautifulSoup(result, 'lxml')
                
                # real time inverter power charts are in a container labelled 'highcharts-series-group' inside a 'rect' element
                real_time_chart_container = soup.find("g", {"class": "highcharts-series-group"}) 
                real_time_inverter_data = real_time_chart_container.find_all('rect')      #each inverter data is contained in a 'rect' element  

                for data in real_time_inverter_data:
                    inverter_data_extracted.append(data['height'])                        #extract column bar heights from highcharts-container on Solar.Web
                
                #Online inverters will have a column-bar height > 0 on the highcharts-container extracted above from Solar.Web
                inverter_data_extracted = pd.to_numeric(inverter_data_extracted, errors='coerce')
                invertersOnline = inverter_data_extracted.astype(bool).sum(axis=0)
                InverterCounter.append(invertersOnline)
                print("InverterCounter successful for {0}: {1} inverter(s) online".format(site,invertersOnline))
                print(" ")
            
            except:
                print("Error: Site page did not load successfully.Inverter counter will assume 0 inverters are online for this site")
                InverterCounter.append(0)
            
        except:
            print("Error: Site page did not load successfully.Inverter counter will assume 0 inverters are online for this site")
            InverterCounter.append(0)  

    except:
        print("Error: Site page did not load successfully.Inverter counter will assume 0 inverters are online for this site")
        InverterCounter.append(0)
    
    #return to Home Page
    browser.find_element_by_xpath('/html/body/nav/div/a[1]/img').click()
    time.sleep(5)
    
#save InverCounter values to dataframe
Froniusdf['Inverters_Online'] = InverterCounter  

#calculate Inverter Availability 
Froniusdf['Inverter_Availability'] = Froniusdf['Inverters_Online']/Froniusdf['Inverters_Installed']
Froniusdf['Inverter_Availability'].fillna(0)

#close browser
browser.close()

#get current date and time to use in output file name
timeString = datetime.datetime.now().strftime("%Y%m%d-%H%M")

#save processed data to excel file and open the excel file
folderSave = Path("OutputFiles")

saveName = timeString + '_Fronius-InverterCounter'
saveLocation = folderSave/saveName
saveLocation = saveLocation.with_suffix(saveLocation.suffix + '.xlsx')

writer =  pd.ExcelWriter(saveLocation, engine='xlsxwriter')
Froniusdf.to_excel(writer, sheet_name="Inverter Counter")
writer.save()

#open excel file
os.startfile(saveLocation)

#exit program
print("**  Fronius Inverter Counter AFL Bot script completed successfully.     **")
print("**                                                                      **")
print("**************************************************************************")
exit
