# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a Fronius Webscrapper script file that reads the current Error Messages on Solar.Web

Created on Fri Dec 12 2019

@author: Li.Kaira
"""
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
from pathlib import Path
import time
import datetime

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#print welcome statement
print("**  Running the Fronius Message Reader AFL Bot script...                **")

#read login credentials from text file
credentials = open('Credentials/credentials.txt', "r")
lines = credentials.readlines()
username = lines[0]
password = lines[1]
credentials.close()

#get current date and time to use in output file name
timeString = datetime.datetime.now().strftime("%Y%m%d-%H%M")

#define output path and filename
folderSave = Path("OutputFiles")
saveName = timeString + 'Fronius-Messages'
saveLocation = folderSave/saveName
saveLocation = saveLocation.with_suffix(saveLocation.suffix + '.xlsx')

#use Selenium to open Fronius webpage and login
print("**  Reading Fronius Service Messages...                                 **")
driver = 'Driver/geckodriver.exe'
browser = webdriver.Firefox(executable_path=driver)
browser.get("https://www.solarweb.com/MessageCenter/ServiceMessages")
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
time.sleep(15)                  #wait for page to load

#accept cookies
try:
    #browser.current_window_handle(browser.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click())
    browser.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()
    time.sleep(3)
except:
    pass

#select 'Show 100' in Message Center page, after waiting 10seconds for page to load
try:
    browser.find_element_by_xpath("//select[@name='js-messageCenter-messages_length']/option[text()='100']").click()
except:
    print("Error: Page load unsuccessful. Program will shutdown")
    exit


#download site html source and extract table
time.sleep(2)
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
merged = pd.concat(output)


#drop unwanted columns
dropCols = ['Data source ID', 'Actions']
merged.drop(dropCols, axis = 1, inplace=True)
print(merged)

#close browser
browser.close()

#save to excel file
writer =  pd.ExcelWriter(saveLocation, engine='xlsxwriter')
merged.to_excel(writer, sheet_name="0-299")
writer.save()

#open excel file
os.startfile(saveLocation)

#exit program
print("**  Fronius Message Reader AFL Bot script completed successfully.       **")
print("**                                                                      **")
print("**************************************************************************")
exit






