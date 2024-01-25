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
    #print(number)
    return number


def find_load_more_button(driver):
    """
    Finds the 'Show more jobs' button

    :param Webdriver driver: Selenium webdriver
    :return: Show More Jobs button element
    :rtype: WebElement
    """
    #print("Finding Button")
    time.sleep(.5)

    # Button changes locations sometimes, hence the try/catch
    try:
        #print('Clicked first button')
        return WebDriverWait(driver, .5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button")))
    except selenium.common.exceptions.TimeoutException:
        try:
            return WebDriverWait(driver, .5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button")))
        except selenium.common.exceptions.TimeoutException:
            # If the button is in neither of the expected places and has moved again, this error message is thrown
            try:
                raise Exception("The button is not in the expected places")
            except Exception as e:
                print(str(e))


def click_load_more(driver):
    """
    Clicks the load more button while printing to terminal what is happening

    :param Webdriver driver: Selenium webdriver
    """
    time.sleep(1)
    load_more_button = find_load_more_button(driver)
    #print("Found Button")
    load_more_button.click()


def close_pop_up(driver):
    """
    If popup shows then close the popup to allow show more button presses

    :param Webdriver driver: Selenium webdriver
    """
    time.sleep(.5)
    WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CLASS_NAME, "CloseButton"))).click()
    try:
        WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CLASS_NAME, "CloseButton"))).click()
    except:
        pass
    #print("Closed Popup")
    return


def load_all_jobs(driver):
    """
    Loads all the jobs by utilising job count and for loop

    :param Webdriver driver: Selenium webdriver
    """
    for i in range(0, job_count//RESULT_PER_PAGE):
        try:
            click_load_more(driver)
        except selenium.common.exceptions.ElementClickInterceptedException: #Catches Exception where popup blocks button
            #print("Found Pop-up")
            close_pop_up(driver)
            click_load_more(driver)
    time.sleep(5)


def click_job_listing(driver, i):
    """
    Clicks a job listing

    :param Webdriver driver: Selenium webdriver
    :param int i: for loop index, counts which job listing should be getting clicked
    """
    xpath1 = "/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[" + str(i + 1) + "]/div/div/div[1]"
    xpath2 = "/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[" + str(i + 1) + "]/div/div/div[1]"
    try:
        try:
            WebDriverWait(driver, .5).until(EC.element_to_be_clickable((By.XPATH, xpath1))).click()
        except selenium.common.exceptions.TimeoutException:
            try:
                WebDriverWait(driver, .5).until(EC.element_to_be_clickable((By.XPATH, xpath2))).click()
            except selenium.common.exceptions.TimeoutException:
                print("Job listing is not correct XPATH")
    except selenium.common.exceptions.ElementClickInterceptedException:  # Catches Exception where popup blocks button
        #print("Found Pop-up")
        close_pop_up(driver)
        time.sleep(1)
        click_job_listing(driver, i)


# Set up the webdriver
driver = webdriver.Chrome()
driver.get(target_url)
#print("Maximizing Window")
driver.maximize_window()
#print("Maximized Window")

job_count = get_job_count(driver)

load_all_jobs(driver)

# Retrieve the page source after loading all content
resp = driver.page_source

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(resp, 'html.parser')

# Extract job details as before
allJobsContainer = soup.find("ul", {"class": "JobsList_jobsList__Ey2Vo"})
allJobs = allJobsContainer.find_all("li")

l = []
o = {}

for i in range(job_count):
    click_job_listing(driver, i)
    specific_resp = driver.page_source
    specific_soup = BeautifulSoup(specific_resp, 'html.parser')
    job_listing_container = specific_soup.find("div", {"class": "JobDetails_jobDetailsContainer__sS1W1"})
    try:
        o["company_name"] = allJobs[i].find("span", {"class": "EmployerProfile_employerName__Xemli"}).text
    except:
        o["company_name"] = None
    try:
        o["job_title"] = allJobs[i].find("a", {"class": "JobCard_seoLink__WdqHZ"}).text
    except:
        o["job_title"] = None
    try:
        o["location"] = allJobs[i].find("div", {"class": "JobCard_location__N_iYE"}).text
    except:
        o["location"] = None
    try:
        o["date_listed"] = allJobs[i].find("div", {"class": "JobCard_listingAge__KuaxZ"}).text
    except:
        o["date_listed"] = None
    try:
        o["long_description"] = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//*[@id=\"app-navigation\"]/div[3]/div[2]/div[2]/div[1]/section/div/div[1]"))).get_attribute(
            "innerText")
    except:
        o["long_description"] = None
    try:
        o["company_overview"] = job_listing_container.find("div", {"class": "JobDetails_companyOverviewGrid__CV62w"}).text
    except:
        o["company_overview"] = None
    try:
        o["salary"] = allJobs[i].find("div", {"class": "JobCard_salaryEstimate___m9kY"}).text
    except:
        o["salary"] = None
    l.append(o)
    o = {}

driver.quit()

# Create a DataFrame and save it to a CSV file
df = pd.DataFrame(l)
df.to_csv('jobs.csv', index=False, encoding='utf-8')
