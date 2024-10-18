import os
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import logging
import sys
import argparse


# setup google sheets
def setup_google_sheets(json_key, spreadsheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    if not os.path.exists(json_key):
        raise Exception("Please create service account and a json key")

    creds = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)
    client = gspread.authorize(creds)

    # the spreadsheet with this name should be already created with at least one sheet
    spreadsheet = client.open(spreadsheet_name).sheet1
    return spreadsheet


# scroll_page scrolls down the page till it reaches the end to load all the companies
def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # calculate new scroll height and compare with the last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scrape_companies(browser, website_link, label):

    # the chrome/firefox driver executables should be in the PATH (env var)
    if browser == "chrome":
        service = ChromeService()
        driver = webdriver.Chrome(service=service)
    elif browser == "firefox":
        service = FirefoxService()
        driver = webdriver.Firefox(service=service)
    else:
        raise Exception("Please choose between chrome or firefox")

    # by scrolling we can only get first 1000 elements so there is no point in scrolling through 1000+ elements because we are loosing data
    # this is why we are using a direct link to get only matching companies and scroll through them
    # in our case there are only 26 companies with the flag F24 abd they fit onto one page, but if more companies match a certain flag we would need to scroll down the page
    driver.get(website_link + "?batch=" + label)
    scroll_page(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    result = []

    companies = soup.find_all('a', attrs={"class": "_company_86jzd_338"})
    logging.info(f"There are {len(companies)} companies in total with the flag {label}")

    for company in companies:
        company_name = company.find('span', {'class': "_coName_86jzd_453"}).text
        company_location = company.find('span', {'class': "_coLocation_86jzd_469"}).text
        company_description = company.find('span', {'class': "_coDescription_86jzd_478"}).text
        result.append((company_name, company_location, company_description))

    driver.quit()
    return result


# write_to_google_sheets writes companies' info to the Google spreadsheet
def write_to_google_sheets(spreadsheet, companies):
    spreadsheet.clear()
    spreadsheet.append_row(["Company Name", "Location", "Description"])

    for company in companies:
        spreadsheet.append_row(company)

    logging.info(f"Written data to google sheet")


# job is started every 6 hours
def job(args):
    logging.info("Started the job")
    try:
        spreadsheet = setup_google_sheets(args.json_key, args.spreadsheet_name)
        companies = scrape_companies(args.browser, args.website, args.label)
        write_to_google_sheets(spreadsheet, companies)
    except Exception as e:
        logging.error(e)

    logging.info("Finished the job")


def process_command_line_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--label",
        default="F24",
        type=str,
        help="The flag that will be matched against the companies",
    )
    parser.add_argument(
        "-n",
        "--spreadsheet-name",
        required=True,
        type=str,
        help="The name of the google sheet to write data to",
    )
    parser.add_argument(
        "-k",
        "--json-key",
        required=True,
        type=str,
        help="The path to the json key to access the google sheets API",
    )
    parser.add_argument(
        "-w",
        "--website",
        default="https://www.ycombinator.com/companies",
        type=str,
        help="A website to scrape the data from",
    )
    parser.add_argument(
        "-b",
        "--browser",
        choices=["chrome", "firefox"],
        default="chrome",
        type=str,
        help="The browser with the selenium extension",
    )
    return parser.parse_args(args)


def main(args=None):
    args = process_command_line_args(args)

    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
    logging.info(
        f"Scraping of the {args.website} and loading the data into {args.spreadsheet_name} has started with the periodicity of 6 hours")
    job(args)
    schedule.every(6).hours.do(job, args)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
