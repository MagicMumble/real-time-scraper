from bs4 import BeautifulSoup
from reportlab.graphics.charts.textlabels import Label
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import logging
from urllib.parse import quote
from selenium.webdriver.common.action_chains import ActionChains
import random
import time
import string

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


def random_pause(min_delay=10, max_delay=30):
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def random_scroll(driver):
    direction = random.choice(["up", "down"])
    scroll_amount = random.randint(100, 800)

    if direction == "down":
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    else:
        driver.execute_script(f"window.scrollBy(0, {-scroll_amount});")

    random_pause(3, 6)


def scroll_down(driver):
    scroll_amount = random.randint(400, 1200)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    random_pause(5, 20)


def scroll_down_periodically(driver):
    for _ in range(int(random.uniform(20, 23))):
        scroll_down(driver)


def scroll_up(driver):
    scroll_amount = random.randint(400, 1200)
    driver.execute_script(f"window.scrollBy(0, {-scroll_amount});")
    random_pause(5, 20)


def random_periodic_scroll(driver):
    action = random.choice(["yes", "no"])
    if action == "yes":
        for _ in range(int(random.uniform(3, 10))):
            random_scroll(driver)


def random_mouse_movement(driver):
    action = ActionChains(driver)

    x_offset = random.randint(-10, 10)
    y_offset = random.randint(-10, 10)

    try:
        action.move_by_offset(x_offset, y_offset).perform()
    except Exception as e:
        print(x_offset, y_offset)

    random_pause(1, 3)


def random_periodic_mouse_movement(driver):
    action = random.choice(["yes", "no"])
    if action == "yes":
        for _ in range(int(random.uniform(2, 4))):
            random_mouse_movement(driver)


def pretend_to_be_a_user(driver):
    random_periodic_scroll(driver)
    random_periodic_mouse_movement(driver)

# before searching the companies we must log in first
def login(email, password, browser):
    driver = get_the_driver(browser)

    driver.get('https://www.linkedin.com/login')
    random_pause(3, 7)

    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(email)
    random_pause(3, 8)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)
    random_pause(2, 6)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    random_pause(2, 4)
    login_button.click()
    random_pause(2, 5)

    # pretend to check my feed
    scroll_down_periodically(driver)
    random_pause(10, 20)

    return driver


def generate_random_word():
    word_length = random.randint(2, 3)

    # Generate a random word with random letters
    random_word = ''.join(random.choice(string.ascii_lowercase) for _ in range(word_length))

    return random_word

def send_random_request(driver, weblink):
    quoted_label = quote(generate_random_word())
    link = f"{weblink}?keywords={quoted_label}"
    driver.get(link)
    pretend_to_be_a_user(driver)
    random_pause(5, 8)

# we are going through the pages until there is no more companies found
def get_companies(driver, label):
    quoted_label = quote(label)
    page_number = 1
    weblink = "https://www.linkedin.com/search/results/companies"
    resulting_companies = []
    while True:
        link = f"{weblink}?keywords={quoted_label}&page={page_number}"
        driver.get(link)
        pretend_to_be_a_user(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        companies = soup.find_all('li', attrs={"class": "reusable-search__result-container"})
        if len(companies) == 0:
            break
        resulting_companies.append(companies)
        page_number += 1
        send_random_request(driver, weblink)

    driver.get("https://www.linkedin.com/feed/")
    scroll_down_periodically(driver)
    random_pause(2, 5)

    companies = [item for sublist in resulting_companies for item in sublist]
    logging.info(f"There are {len(companies)} companies in total on the LinkedIn website with the flag {label}")
    return companies


# here we get the name and the description of each company
def parse_companies(companies):
    result = []
    for company in companies:
        company_name = company.find('span', {'class': "entity-result__title-text"}).text
        company_description = company.find('p', {'class': "entity-result__summary--2-lines"}).text
        result.append((company_name.replace('\n', ''), company_description.replace('\n', '')))
    return result


# scrape_LinkedIn_companies logs into LinkedIn, searches for the companies with the desired flag end returns scraped companies
def scrape_LinkedIn_companies(args, linkedInDriver):
    companies = get_companies(linkedInDriver, args.linkedIn_tag)
    result = parse_companies(companies)
    return result