import pandas as pd
import datetime
from pathlib import Path

def save_pd_data_frame_to_csv(pd_data_frame, name_append): 
    #get current date and time to use in output file name   
    timeString = datetime.datetime.now().strftime("%Y%m%d-%H%M") 
    
    #save processed data to excel file
    folderSave = Path("Output")
    saveName = timeString + name_append    
    saveLocation = folderSave/saveName    
    pd_data_frame.to_csv(saveLocation, sep=',', encoding='utf-8', index=False)