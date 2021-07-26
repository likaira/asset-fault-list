import time
import pandas as pd
from bs4 import BeautifulSoup
from run_browser import open_browser

#define a function to login to EnnexOS
def login_to_portal(browser, username, password):
    try: #Accept cookies (if Cookies banner exists)
        browser.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
        time.sleep(1)
    except:
        pass
    browser.find_element_by_name("username").send_keys(username)
    browser.find_element_by_name("password").send_keys(password)
    time.sleep(2)
    browser.find_element_by_tag_name("button").click()

#define a function to download system generation data from ennexOS
def download_data(url, username, password):
    try: 
        browser =  open_browser(url)          
        try:
            login_to_portal(browser=browser, username=username, password=password)
        except:
            print("**  Error: Login unsuccessful. Program will shutdown                       **")            
            browser.close()
            return 0

        #download site html source and extract table
        time.sleep(10)
        result = browser.page_source
        soup = BeautifulSoup(result, 'lxml')        
        table = soup.find_all('table')
        data = pd.read_html(str(table))
        ennexdf = data[0]        
        #get previous day generation values in [kWh]
        generation = ennexdf.iloc[:,-5]
        generation = pd.to_numeric(generation, errors='coerce')
        generation.fillna(0)
        total = generation.sum()    
        browser.close()    
    except:
        #if page does not load, use 0kWh as total generation     
        print("**  Error: Page load unsuccessful.                             **")    
        total = 0
    return total
