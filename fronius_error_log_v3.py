# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a Fronius Webscrapper script file that reads the current Error Messages on Solar.Web

v3 - Updated to run on Raspberry Pi in headless mode

Created on Fri Dec 12 2019

@author: Li.Kaira
"""
from run_browser import open_browser
from login_to_portal import login_to_solarweb
from save_to_csv import save_pd_data_frame_to_csv
from bs4 import BeautifulSoup
import pandas as pd
import os
import time


#print welcome statement
print("**  Running the Fronius Message Reader AFL Bot script...                **")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read login credentials from Environment variables
username = os.environ.get('FRONIUS_USERNAME')
password = os.environ.get('FRONIUS_PASSWORD')



#use Selenium to open Fronius webpage and login
print("**  Reading Fronius Service Messages...                                 **")

#open Fronius Solar Web 
browser = open_browser("https://www.solarweb.com/MessageCenter/ServiceMessages")

#accept cookies
try:
    browser.find_element_by_xpath("/html/body/header/div[1]/div/p[2]/button").click()
    time.sleep(3)
except:
    pass

#login to Solar Web 
login_to_solarweb(browser=browser, username=username, password=password)
time.sleep(10)                  #wait for page to load

#accept cookies
try:
    browser.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()
    time.sleep(3)
except:
    pass

#select 'Show 100' in Message Center page, then filter by 'Last 30 days'
try:
    browser.find_element_by_xpath("//select[@name='js-messageCenter-messages_length']/option[text()='100']").click()
    time.sleep(5)
    try:
        # browser.find_element_by_xpath("/html/body/div[5]/div[1]/ul/li[2]").click()
        browser.find_element_by_css_selector('.ranges > ul:nth-child(1) > li:nth-child(2)').click()
    except:
        pass
except:
    print("Error: Page load unsuccessful. Program will shutdown")
    exit


#download site html source and extract table
time.sleep(10)
result = browser.page_source
soup = BeautifulSoup(result, 'lxml')
table = soup.find_all('table')
data = pd.read_html(str(table))
fm_1 = data[0]

#click 'Next' to view next 100 error messages
try:
    browser.find_element_by_xpath("//*[@id='js-messageCenter-messages_next']/a").click()

except:
    print("Error: Next click didn't work")
    exit

#download site html source and extract table
time.sleep(2)
result = browser.page_source
soup = BeautifulSoup(result, 'lxml')
table = soup.find_all('table')
data = pd.read_html(str(table))
fm_2 = data[0]

#click 'Next' to view next 100 error messages
try:
    browser.find_element_by_xpath("//*[@id='js-messageCenter-messages_next']/a").click()

except:
    print("Error: Next click didn't work")
    exit

#download site html source and extract table
time.sleep(2)
result = browser.page_source
soup = BeautifulSoup(result, 'lxml')
table = soup.find_all('table')
data = pd.read_html(str(table))
fm_3 = data[0]


#concat 300 most recent error messages
output = [fm_1, fm_2, fm_3]
ErrorLogDF = pd.concat(output)


#drop unwanted columns
dropCols = ['Data source ID', 'Actions']
ErrorLogDF.drop(dropCols, axis = 1, inplace=True)
print(ErrorLogDF)

#close browser
browser.close()

#save processed data to csv file 
save_pd_data_frame_to_csv(pd_data_frame=ErrorLogDF, name_append='_Fronius-ErrorLog')

#exit program
print("**  Fronius Message Reader AFL Bot script completed successfully.       **")
print("**                                                                      **")
print("**************************************************************************")
exit






