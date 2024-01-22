from bs4 import BeautifulSoup
from selenium import webdriver
import time




l=list()
o={}

target_url = "https://www.glassdoor.com/Job/new-york-python-jobs-SRCH_IL.0,8_IC1132348_KO9,15.htm?clickSource=searchBox"

driver=webdriver.Chrome()

driver.get(target_url)

driver.maximize_window()
time.sleep(2)

resp = driver.page_source

driver.close()