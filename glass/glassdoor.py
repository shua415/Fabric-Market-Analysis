from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd

l=list()
o={}

target_url = "https://www.glassdoor.com/Job/new-york-python-jobs-SRCH_IL.0,8_IC1132348_KO9,15.htm?clickSource=searchBox"
driver=webdriver.Chrome()
driver.get(target_url)
driver.maximize_window()
time.sleep(5)
resp = driver.page_source
driver.close()

soup=BeautifulSoup(resp,'html.parser')

allJobsContainer = soup.find("ul",{"class":"JobsList_jobsList__Ey2Vo"})
allJobs = allJobsContainer.find_all("li")
for job in allJobs:
    try:
        o["name-of-company"]=job.find("span",{"class":"EmployerProfile_employerName__Xemli"}).text
    except:
        o["name-of-company"]=None
    try:
        o["name-of-job"]=job.find("a",{"class":"JobCard_seoLink__WdqHZ"}).text
    except:
        o["name-of-job"]=None
    try:
        o["location"]=job.find("div",{"class":"JobCard_location__N_iYE"}).text
    except:
        o["location"]=None
    try:
        o["salary"]=job.find("div",{"class":"JobCard_salaryEstimate___m9kY"}).text
    except:
        o["salary"]=None
    l.append(o)
    o={}

print(l)

df = pd.DataFrame(l)
df.to_csv('jobs.csv', index = False, encoding = 'utf-8')