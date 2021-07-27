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
from run_browser import open_browser
from login_to_portal import login_to_solarweb
from save_to_csv import save_pd_data_frame_to_csv
from bs4 import BeautifulSoup
import pandas as pd
import os
import time


#print welcome statement
print("**  Running the Fronius Inverter Counter AFL Bot script...              **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
username = os.environ.get('FRONIUS_USERNAME')
password = os.environ.get('FRONIUS_PASSWORD')

  
#open Fronius Solar Web 
browser = open_browser("https://www.solarweb.com/PvSystems/Widgets")


#accept cookies
try:
    browser.find_element_by_xpath("/html/body/header/div[1]/div/p[2]/button").click()
    time.sleep(3)
except:
    pass

#login to Solar Web and select 'Show All' in 'PV System Overview' page
login_to_solarweb(browser=browser, username=username, password=password)
time.sleep(10)
browser.find_element_by_xpath("//select[@name='js-pvsystem-table-id_length']/option[text()='All']").click()

#download site html source and extract table
time.sleep(2)
result = browser.page_source
soup = BeautifulSoup(result, 'lxml')
table = soup.find_all('table')
data = pd.read_html(str(table))
Froniusdf = data[0]

#drop unwanted columns
dropCols = ['Unnamed: 0', 'kWh/kWp', 'kWh Today', 'Last update', 'Errors (today)']
Froniusdf.drop(dropCols, axis = 1, inplace=True)

#rename 'Inv.' column to 'Inverters_Installed'
Froniusdf = Froniusdf.rename(columns = {'Inv.' : 'Inverters_Installed'})

#iterate through all PV systems and extract number of inverters online
print("**  InverterCounter is running...                                       **")
print("**                                                                      **")
InverterCounter = []

for site in Froniusdf['PV system'][0:3]:                 
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


#save processed data to csv file 
save_pd_data_frame_to_csv(pd_data_frame=Froniusdf, name_append='_Fronius-InverterCounter')


#exit program
print("**  Fronius Inverter Counter AFL Bot script completed successfully.     **")
print("**                                                                      **")
print("**************************************************************************")
exit
