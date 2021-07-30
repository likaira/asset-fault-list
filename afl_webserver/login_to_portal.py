import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#define a function to login to Sunny Portal
def login_to_sma(browser, username, password):
    browser.find_element_by_id("txtUserName").send_keys(username)
    browser.find_element_by_id("txtPassword").send_keys(password)
    browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_Logincontrol1_MemorizePassword"]').click()
    time.sleep(2)
    browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_Logincontrol1_LoginBtn"]').click()


#define a function to login to EnnexOS
def login_to_ennexOS(browser, username, password):
    try: #Accept cookies (if Cookies banner exists)
        browser.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
        time.sleep(1)
    except:
        pass
    browser.find_element_by_name("username").send_keys(username)
    browser.find_element_by_name("password").send_keys(password)
    time.sleep(2)
    browser.find_element_by_tag_name("button").click()


#define a function to login to SolarWeb
def login_to_solarweb(browser, username, password):    
    browser.find_element_by_id("username").send_keys(username)
    browser.find_element_by_id("password").send_keys(password)
    try:
        browser.find_element_by_xpath('//*[@id="loginForm"]/fieldset/p[2]/label').click()
    except:
        pass
    time.sleep(3)
    browser.find_element_by_id("submitButton").click()
    time.sleep(10)    
    #accept cookies
    try:        
        browser.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept").click()
        time.sleep(3)
    except:        
        pass
    

#define a function to login to Solar Analytics
def login_to_solar_analytics(browser, username, password):  
    browser.find_element_by_id("email").send_keys(username)
    browser.find_element_by_id("password").send_keys(password)    
    time.sleep(2)
    browser.find_element_by_xpath('/html/body/div/div/div/div[2]/div/form/div[5]/div/button').click()
    time.sleep(5)                  #wait for page to load