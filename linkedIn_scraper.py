from bs4 import BeautifulSoup
from reportlab.graphics.charts.textlabels import Label
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import logging
from urllib.parse import quote

# get_the_driver returns the right driver corresponding to the desired browser
def get_the_driver(browser):

    # the chrome/firefox driver executables should be in the PATH (env var)
    if browser == "chrome":
        service = ChromeService()
        driver = webdriver.Chrome(service=service)
    elif browser == "firefox":
        service = FirefoxService()
        driver = webdriver.Firefox(service=service)
    else:
        raise Exception("Please choose between chrome or firefox")
    return driver


# before searching the companies we must log in first
def login(email, password, browser):
    driver = get_the_driver(browser)

    driver.get('https://www.linkedin.com/login')

    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(email)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    return driver


# we are going through the pages until there is no more companies found
def get_companies(driver, label):
    quoted_label = quote(label)
    page_number = 1
    weblink = "https://www.linkedin.com/search/results/companies"
    resulting_companies = []
    while True:
        link = f"{weblink}?keywords={quoted_label}&page={page_number}"
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        companies = soup.find_all('li', attrs={"class": "reusable-search__result-container"})
        if len(companies) == 0:
            break
        resulting_companies.append(companies)
        page_number += 1

    driver.quit()
    logging.info(f"There are {len(resulting_companies)} companies in total on the LinkedIn website with the flag {label}")
    return resulting_companies


# here we get the name and the description of each company
def parse_companies(companies):
    result = []
    for company in companies:
        company_name = company.find('span', {'class': "entity-result__title-text"}).text
        company_description = company.find('p', {'class': "entity-result__summary--2-lines"}).text
        result.append((company_name.replace('\n', ''), company_description.replace('\n', '')))
    return result


# scrape_LinkedIn_companies logs into LinkedIn, searches for the companies with the desired flag end returns scraped companies
def scrape_LinkedIn_companies(args):
    driver = login(args.linkedIn_email, args.linkedIn_password, args.browser)
    companies = get_companies(driver, args.linkedIn_tag)
    companies = [item for sublist in companies for item in sublist]
    result = parse_companies(companies)
    return result