# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a Solaredge API script file, used to get Open Site Alerts
https://www.solaredge.com/sites/default/files/se-monitoring-platform-b2b-api-update-application-note.pdf

"""
import requests as rq
import json as js
import os

#get API_KEY from Environment variables
API_KEY = os.environ.get('SE_API_KEY')

#print program introduction
print("This program returns the list of open alerts for the site provided")

#enter site(s) id
siteId = input("Enter site ID: ")

#build url
#-------------------------------------------------
url1 = "https://monitoringapi.solaredge.com/site/"
url2 = siteId
url3 = "/details?"
url4 = "&api_key="
url = url1 + url2 + url3 + url4 + API_KEY
#-------------------------------------------------

response = rq.get(url)
#Check if valid response is received and print output
if response.status_code == 200:
    parsed = js.loads(response.content)         
    print(js.dumps(parsed, indent=4, sort_keys=True))
else:
    print("Error running API - please check API documentation for any changes")

#prompt user to close program
input("Press enter to exit")

