#Setup Python Script to use the Django ORM
#https://docs.djangoproject.com/en/3.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afl_webserver.settings")
django.setup()

#Proceed to import required modules from Django app
from main.models import PVSystem
import pandas as pd

print("Starting batch upload...")

#read csv file with PV system names into pandas dataframe
link_to_file = '/home/pi/Documents/Code/AFL/asset-fault-list/Inputs/se.csv'
pv_systems_df = pd.read_csv(link_to_file, header=0)
iterate_rows = pv_systems_df.iterrows()

#create list of objects to upload to Database, model - PVSystem
objs = [
    PVSystem(
        name = row['name'],
        inverter = row['inverter'],
        link_to_portal = row['link_to_portal'],
        # link_to_salesforce = row['link_to_salesforce'],
        dc_size = row['dc_size'],
        # ac_size = row['dc_size'],        
        # bom_id = row['bom_id'],        
        # vendor = row['vendor']            
    )
    for index, row in iterate_rows
]

#bulk create objects
#https://docs.djangoproject.com/en/3.2/ref/models/querysets/#bulk-create
PVSystem.objects.bulk_create(objs)

print("Batch upload complete")