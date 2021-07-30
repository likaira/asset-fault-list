from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time

#define a function to open a webbrowser using Selenium
def open_browser(page):    
    options = Options()
    options.headless = True
    browser = Firefox(options=options) 
    try:
        browser.get(page)
        time.sleep(5)
    except:
        time.sleep(30)
        browser.get(page)
    return browser