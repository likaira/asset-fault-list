#Setup Python Script to use the Django ORM
#https://docs.djangoproject.com/en/3.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage
import django
from django.conf import settings
from main import main_defaults

settings.configure(default_settings=main_defaults, DEBUG=True)
django.setup()

#Proceed to import required modules from Django app
from main import models
import pandas as pd

#read csv file with PV system names into pandas dataframe
link_to_file = '/home/pi/Documents/Code/AFL/asset-fault-list/Inputs/ennex_db_upload.csv'
pv_systems_df = pd.read_csv(link_to_file, header=0)
iterate_rows = pv_systems_df.iterrows()

#create list of objects to upload to Database, model - PVSystem
objs = [
    PVSystem(
        name = row['name'],
        inverter = row['inverter'],
        link_to_portal = row['link_to_portal'],
        bom_id = row['bom_id'],
        dc_size = row['dc_size']
    )
    for index, row in iterate_rows
]

#bulk create objects
#https://docs.djangoproject.com/en/3.2/ref/models/querysets/#bulk-create
PVSystem.objects.bulk_create(objs)