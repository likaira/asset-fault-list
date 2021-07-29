#Python Libraries Imports
import pandas as pd

#Local libraries
from models import PVSystem

#read csv file with PV system names into pandas dataframe
link_to_file = '/home/pi/Documents/Code/AFL/asset-fault-list/Inputs/fronius.csv'
pv_systems_df = pd.read_csv(link_to_file, header=0)
iterate_rows = pv_systems_df.iterrows()

#create list of objects to upload to Database, model - PVSystem
objs = [
    PVSystem(
        name = row['name'],
        inverter = row['inverter']
    )
    for index, row in iterate_rows
]

#bulk create objects
#https://docs.djangoproject.com/en/3.2/ref/models/querysets/#bulk-create
PVSystem.objects.bulk_create(objs)