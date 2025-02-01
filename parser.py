import time

import requests
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent
from fake_useragent import FakeUserAgentError
from math import ceil
from random import randint
from time import sleep
from base64 import b64decode
from io import BytesIO
from PIL import Image
import pytesseract
from webdriver_manager.chrome import ChromeDriverManager
import config

URL_DATA = f"https://food.databdn.com/#/app/database/allContinents/allCountries/dairy/allEntries/"
# CATEGORY = 'Beer Importers'
# CATEGORY = 'Beer Distributors'
CATEGORY = 'Dairy Products'


def get_details(driver, n):
    # get details
    details_list = []
    details_categories_list = []
    for row_number in range(1, n+1):
        # read contact info
        # time.sleep(0.2)
        status = False
        while not status:
            try:
                xpath = f'/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{row_number}]/td[1]/a[1]'
                button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", button)
                status = True
            except:
                print('repeat open find')
                status = False
                time.sleep(0.1)
                pass

        time.sleep(0.5)
        # details = driver.find_element(by=By.XPATH, value='/html/body/div[4]/div[2]/div/div[2]/div/div[2]')
        status = False
        while not status:
            try:
                # details_xpath = '/html/body/div[4]/div[2]/div/div[2]/div'
                detail_xpath = '/html/body/div[4]/div[2]/div/div[2]'
                details = WebDriverWait(driver, 100).until(
                    EC.visibility_of_element_located((By.XPATH, detail_xpath)))
                details = details.get_attribute('outerHTML')
                status = True
            except:
                print('repeat details')
                status = False
                time.sleep(0.1)
                pass
        if len(details) > 1:
            details_list.append(details)

        # read categories
        time.sleep(0.2)
        status = False
        while not status:
            try:
                xpath = f'/html/body/div[4]/div[2]/div/div[2]/ul/li[2]/a'
                button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", button)
                status = True
            except:
                print('repeat open window')
                status = False
                time.sleep(0.1)
                pass

        # read categories
        time.sleep(0.3)
        # details_categories = driver.find_element(by=By.XPATH, value='/html/body/div[4]/div[2]/div/div[2]/div/div[2]')
        details_categories = None

        status = False
        while not status:
            try:
                # category_xpath = '/html/body/div[4]/div[2]/div/div[2]/div/div[2]'
                category_xpath = '/html/body/div[4]/div[2]/div/div[2]'
                details_categories = WebDriverWait(driver, 100).until(
                    EC.visibility_of_element_located((By.XPATH, category_xpath)))
                details_categories = details_categories.get_attribute('outerHTML')
                status = True
            except:
                print('repeat categories')
                status = False
                time.sleep(0.1)
                pass
        if len(details_categories) > 1:
            details_categories_list.append(details_categories)

        # close menu
        # time.sleep(0.5)
        status = False
        while not status:
            try:
                button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ngdialog-close')))
                driver.execute_script("arguments[0].click();", button)
                status = True
            except:
                print('repeat close window')
                status = False
                time.sleep(0.1)
                pass

    details_list.append('')
    details_categories_list.append('')
    return details_list, details_categories_list


def main_parser(category, section):
    try:
        ua = UserAgent().chrome
    except FakeUserAgentError:
        ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(15)
    driver.get(URL_DATA)

    driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div[1]/form/div[2]/div[1]/input").send_keys(
        config.USERNAME)
    driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div[1]/form/div[2]/div[2]/input").send_keys(
        config.PASSWORD)
    driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div[1]/form/button").click()

    # close reniew subscription
    time.sleep(2)
    # button = driver.find_element(by=By.ID, value='ngdialog-close')
    # driver.execute_script("arguments[0].click();", button)
    driver.back()
    driver.get(f'https://food.databdn.com/#/app/database/allContinents/allCountries/{section}/allEntries/')

    time.sleep(2)
    # driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[2]/div/li[1]/a").click()
    # driver.find_element(by=By.PARTIAL_LINK_TEXT, value=category).click()

    # select all columns
    driver.implicitly_wait(1)
    driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/button").click()
    driver.find_element(by=By.CLASS_NAME, value='ColVis_ShowAll').click()
    xOffset = 100
    yOffset = 100
    # Performs mouse move action onto the element
    webdriver.ActionChains(driver).move_by_offset(xOffset, yOffset).click().perform()

    # select all categories

    driver.implicitly_wait(1)
    driver.find_element(by=By.XPATH,
                        value='/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/div[5]/div[2]/a[2]').click()

    # get number of pages
    driver.implicitly_wait(1)
    time.sleep(2)
    count = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[1]/strong')
    time.sleep(2)
    count = count.text.replace(',', '')
    count = int(count)
    driver.implicitly_wait(1)
    pages = ceil(count / 20)

        # read first page
    df = pd.DataFrame()
    all_tables = pd.read_html(driver.page_source, attrs={'id': 'bfi-table'})
    contacts, categories = get_details(driver, n=20)
    all_tables[0]['Contacts'] = contacts
    all_tables[0]['Categories'] = categories
    df = pd.concat([df, all_tables[0]], axis=0)
    print(df.shape)

    filename = category.lower().replace(' ', '_')
    # list other pages
    for i in range(2, pages + 1):
        button = driver.find_element(by=By.ID, value='bfi-table_next')
        driver.execute_script("arguments[0].click();", button)

        number_of_rows = min(20, count - i*20)
        driver.implicitly_wait(1)
        all_tables = pd.read_html(driver.page_source, attrs={'id': 'bfi-table'})
        contacts, categories = get_details(driver, n=number_of_rows)
        all_tables[0]['Contacts'] = contacts
        all_tables[0]['Categories'] = categories
        df = pd.concat([df, all_tables[0]], axis=0)
        print(df.shape)
        time.sleep(2)
        df.to_csv(f'results/{section}/{filename}.csv', index=False)
        # # reset previous mouse position
        # xOffset = 100
        # yOffset = 0
        # # Performs mouse move action onto the element
        # webdriver.ActionChains(driver).move_by_offset(xOffset, yOffset).click().perform()

    df.to_csv(f'results/{filename}.csv', index=False)
    print(df.shape)

    driver.quit()


if __name__ == "__main__":
    main_parser('Dairy Products', 'dairy')
    # main_parser('Beer Distributors')
    # main_parser('Beer Retailers')
