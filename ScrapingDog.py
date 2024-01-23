import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

RESULT_PER_PAGE = 30
target_url = "https://www.glassdoor.com/Job/new-zealand-data-engineer-jobs-SRCH_IL.0,11_IN186_KO12,25.htm"


def get_job_count(driver):
    """
    Gets Job Count from '___ results found' text

    :param Webdriver driver: Selenium webdriver
    :return: the number of jobs
    :rtype: int
    """
    text = driver.find_element(By.CLASS_NAME, "SearchResultsHeader_jobCount__12dWB").text
    job_count = split_job_count(text)
    return job_count


def split_job_count(s):
    """
    Takes the string from get_job_count and separates the number from the string

    :param string s: Full string from webpage '___ results found'
    :return: the number inside the string
    :rtype: int
    """
    number = [int(word) for word in s.split() if word.isdigit()][0]
    print(number)
    return number


def find_load_more_button(driver):
    """
    Finds the 'Show more jobs' button

    :param Webdriver driver: Selenium webdriver
    :return: Show More Jobs button element
    :rtype: WebElement
    """
    print("Finding Button")
    time.sleep(.5)

    # Button changes locations sometimes, hence the try/catch
    try:
        print('Clicked first button')
        return WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button")))
    except selenium.common.exceptions.TimeoutException:
        print("Clicked second button")
        return WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button")))


def click_load_more(driver):
    """
    Clicks the load more button while printing to terminal what is happening

    :param Webdriver driver: Selenium webdriver
    """
    time.sleep(1)
    load_more_button = find_load_more_button(driver)
    print("Found Button")
    print(type(load_more_button))
    load_more_button.click()


def close_pop_up(driver):
    """
    If popup shows then close the popup to allow show more button presses

    :param Webdriver driver: Selenium webdriver
    """
    time.sleep(.5)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "CloseButton"))).click()
    print("Closed Popup")
    return


def load_all_jobs(driver):
    """
    Loads all the jobs by utilising job count and for loop

    :param Webdriver driver: Selenium webdriver
    """
    for i in range(0, get_job_count(driver)//RESULT_PER_PAGE):
        try:
            click_load_more(driver)
        except selenium.common.exceptions.ElementClickInterceptedException: #Catches Exception where popup blocks button
            print("Found Pop-up")
            close_pop_up(driver)
            click_load_more(driver)
    time.sleep(5)


# Set up the webdriver
driver = webdriver.Chrome()
driver.get(target_url)
print("Maximizing Window")
driver.maximize_window()
print("Maximized Window")

load_all_jobs(driver)

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
