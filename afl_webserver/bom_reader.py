import pandas as pd
import datetime, time
from progress.bar import Bar
from run_browser import open_browser
from bs4 import BeautifulSoup

def get_bom_data(link_to_stationIds):
    #import station Ids from external csv file and format to be 6 digits long
    stationId = pd.read_csv(link_to_stationIds, header=0)
    stationId['Id']=stationId['Id'].apply(lambda x: '{0:0>6}'.format(x)) 

    #add unique station url to stationId dataframe
    base_url = "http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=193&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num="
    stationId['url'] = base_url + stationId['Id']

    #get day and month for use in extracting yesterday's radiation data
    today = datetime.date.today()
    month = today.month
    day=today.day

    #initiliase counter
    index = 0
    irrad_yday = []

    #Open bom.gov.au,extract values Solar exposure tables and save as a new colum in stationId dataframe
    bar = Bar('Downloading data from BOM.gov.au', max = len(stationId['Id']))

    for url in stationId['url']:        
        try:
            browser = open_browser(url)
            time.sleep(10)
            BOMdata = browser.page_source
            soup = BeautifulSoup(BOMdata, 'lxml')    
            BOMtable = soup.find_all('table')[0]
            BOMdf = pd.read_html(str(BOMtable))[0]
            irrad_value = BOMdf.iat[day-1,month]/3.6                    
            #irrad_value = BOMdf.iat[30,9]
            irrad_yday.append(irrad_value) 
            browser.close() 
        except:
            print("**  Error: Page load unsuccessful.                        **")
            irrad_value = 0 
            irrad_yday.append(irrad_value) 
            browser.close()            
        index = index + 1
        bar.next()

    stationId['irrad_yday'] = irrad_yday
    bar.finish()
    return stationId

#Ability for module to run as a main program
if __name__=="__main__":
    link_to_stationIds = "Inputs/test_bom_urls.csv"
    bom_data = get_bom_data(link_to_stationIds)