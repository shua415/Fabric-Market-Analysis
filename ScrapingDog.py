from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# Function to scroll to the bottom of the page
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Adjust the delay based on the time it takes for new content to load

# Function to click the "Load more" button
# def click_load_more(driver):
#     try:
#         load_more_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button")
#         load_more_button.click()
#         time.sleep(3)  # Adjust the delay based on the time it takes for new content to load
#         return True
#     except:
#         return False

def click_load_more(driver):
    time.sleep(3)
    load_more_button = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button")
    load_more_button.click()
    time.sleep(3)  # Adjust the delay based on the time it takes for new content to load


# Set up the webdriver
target_url = "https://www.glassdoor.com/Job/new-zealand-ai-jobs-SRCH_IL.0,11_IN186_KO12,14.htm"
driver = webdriver.Chrome()
driver.get(target_url)
driver.maximize_window()

# Initial scroll to load some content
scroll_to_bottom(driver)

# Click the "Load more" button until it's not available
for i in range  (1,10):
    click_load_more(driver)
    scroll_to_bottom(driver)

# Retrieve the page source after loading all content
resp = driver.page_source
driver.quit()

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(resp, 'html.parser')

# Extract job details as before
allJobsContainer = soup.find("ul", {"class": "JobsList_jobsList__Ey2Vo"})
allJobs = allJobsContainer.find_all("li")

l = []
o = {}

for job in allJobs:
    try:
        o["name-of-company"] = job.find("span", {"class": "EmployerProfile_employerName__Xemli"}).text
    except:
        o["name-of-company"] = None
    try:
        o["name-of-job"] = job.find("a", {"class": "JobCard_seoLink__WdqHZ"}).text
    except:
        o["name-of-job"] = None
    try:
        o["location"] = job.find("div", {"class": "JobCard_location__N_iYE"}).text
    except:
        o["location"] = None
    try:
        o["salary"] = job.find("div", {"class": "JobCard_salaryEstimate___m9kY"}).text
    except:
        o["salary"] = None
    l.append(o)
    o = {}

# Create a DataFrame and save it to a CSV file
df = pd.DataFrame(l)
df.to_csv('jobs.csv', index=False, encoding='utf-8')
