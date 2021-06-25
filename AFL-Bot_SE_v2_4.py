# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 16:59:39 2019

@author: Li.Kaira

This script reads the SolarEdge daily report file and extracts data
v2 reads files autosaved in 'Verdia Pty Ltd/Operations Team - Asset Management/SolarEdge Fault Reports'
v2.1 updated to read faults raised from Thursday, on a Monday due to Verdia being closed on Fridays
v2.2 updated to remove pandas datetime module and used python datetime module due to pandas datetime becoming deprecated
v2.3 updated Site Name column name to match SE new name
v2.4 updated column names to match the new names used by SE
     removed the 'Last triggered on' column
"""

from pathlib import Path
import pandas as pd
import datetime
# from pandas.tseries.offsets import BDay
import sys,os

#print welcome statement
print("**  Running the SolarEdge AFL Bot script...                             **")

#create datetime objects
today = datetime.date.today()
todayString = today.strftime("%Y%m%d")

#Change working directory to directory of script file
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

#read the raw SolarEdge daily summary report
try:
    folderRead = Path("RawData")
    readLocation = folderRead/todayString
    readLocation = readLocation.with_suffix(readLocation.suffix + '.xlsx')
    Daily_Summary = pd.read_excel(readLocation)
except:
    print(" ")
    print(" ")
    print("ERROR: SolarEdge raw data file not found. The file was not received from the server")
    print("Manually download the file from 'https://monitoring.solaredge.com/solaredge-web/p/home#/reports' under SE-AFL-DailyReport")
    print("Click on 'Saved Reports'; Select the 'SE-AFL-DailyReport' and click 'Generate'")
    print("Save the file in APIs/SolarEdge/RawData as todays date (yyyymmdd)")
    print(" ")
    print(" ")
    print("Program will now shutdown.")
    sys.exit()
    
#remove empty rows - the first 9 rows in file
Daily_Summary.drop(Daily_Summary.index[0:8],inplace=True)

#rename columns
header = Daily_Summary.iloc[0]
Daily_Summary = Daily_Summary[1:]
Daily_Summary.rename(columns=header,inplace=True)

#drop unwanted columns
try:
    columns = ['#', 'Peak Power (kWp)', 'Highest Alert Impact', 'Impact', 'Total Open']
    Daily_Summary.drop(columns, axis = 1, inplace=True)
except:
    columns = ['#', 'Peak Power (kWp)', 'REF::JS_Ext.solaredge.AdminPanel.msgType', 'Total Open']
    Daily_Summary.drop(columns, axis = 1, inplace=True)    

#fill empty values 
try:
    Daily_Summary['Site Name'].fillna(method='ffill', inplace=True)
except:
    Daily_Summary['REF::JS_Ext.solaredge.SiteTable.name'].fillna(method='ffill', inplace=True)
Daily_Summary['Account'].fillna(method='ffill', inplace=True)

#convert string values to date-time values
Daily_Summary['First triggered on'] = pd.to_datetime(Daily_Summary['First triggered on'])

#sort by 'First Triggered on' 
Daily_Summary.sort_values(by=['First triggered on'], inplace=True, ascending=False)

#Return the day of the week as an integer, where Monday is 0 and Sunday is 6. 
weekday_today = today.weekday()

#filter faults raised on last business day
if weekday_today == 0:
    yday = today - datetime.timedelta(days=3) 
    yday = pd.to_datetime(yday)

else:
    yday = today - datetime.timedelta(days=1) 
    yday = pd.to_datetime(yday)
newFaults = Daily_Summary.loc[Daily_Summary['First triggered on'] > yday]
            
#get current date and time to use in output file name
timeString = datetime.datetime.now().strftime("%Y%m%d-%H%M")

#save processed data to excel file
folderSave = Path("OutputFiles")
saveName = timeString + '_SE-Output'
saveLocation = folderSave/saveName
saveLocation = saveLocation.with_suffix(saveLocation.suffix + '.xlsx')

writer = pd.ExcelWriter(saveLocation, engine='xlsxwriter')
newFaults.to_excel(writer, sheet_name="New Faults")
Daily_Summary.to_excel(writer, sheet_name="All Sites")
writer.save() 

#open file
os.startfile(saveLocation)

#exit program
print("**  SolarEdge AFL Bot script completed successfully.                    **")
print("**                                                                      **")
print("**************************************************************************")
exit
