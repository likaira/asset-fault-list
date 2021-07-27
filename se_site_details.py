# -*- coding: utf-8 -*-
"""
Spyder Editor

Site Energy - Time Period

This is a Solaredge API script file to 
"""
import requests as rq
import json as js
import os

#get API_KEY from Environment variables
API_KEY = os.environ.get('SE_API_KEY')

#print program introduction
print("This program returns the details of a site such as name, locations, active alerts etc")

#enter site(s) id
siteId = input("Enter site ID: ")

#build url
#-------------------------------------------------
url1 = "https://monitoringapi.solaredge.com/site/"
url2 = siteId
# url3 = "/details?"
url3 = "/alerts?Status=Open"
url4 = "&api_key="
url = url1 + url2 + url3 + url4 + API_KEY
#-------------------------------------------------

response = rq.get(url)
#Check if valid response is received and print output
if response.status_code == 200:
    parsed = js.loads(response.content)         
    print(js.dumps(parsed, indent=4, sort_keys=True))
else:
    print("Error running API - please check Site Id and API KEY are valid")

#prompt user to close program
input("Press enter to exit ;)")

