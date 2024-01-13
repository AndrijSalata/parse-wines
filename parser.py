import time

import requests
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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

URL_DATA = f"https://wine.databdn.com/#/app/database/allContinents/allCountries/allCategories/allEntries/"
CATEGORY = 'Beer Importers'


def main_parser():
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

    time.sleep(1)
    # driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[2]/div/li[1]/a").click()
    driver.find_element(by=By.PARTIAL_LINK_TEXT, value=CATEGORY).click()

    driver.implicitly_wait(1)
    driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/button").click()
    # iframe = driver.find_element(by=By.XPATH, value="/html/body/ul")
    # driver.switch_to.frame(iframe)
    driver.find_element(by=By.CLASS_NAME, value='ColVis_ShowAll').click()

    xOffset = 100
    yOffset = 100
    # Performs mouse move action onto the element
    webdriver.ActionChains(driver).move_by_offset(xOffset, yOffset).click().perform()
    # ActionChains(driver).move_to_element(driver.find_element(by=By.CLASS_NAME, value='ColVis_ShowAll')).click().perform()
    # driver.find_element_by_class_name('/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/div[5]/div[2]/a[1]').click()
    # '/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div/table'

    # get number of pages
    driver.implicitly_wait(1)
    time.sleep(2)
    count = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[1]/strong')
    time.sleep(2)
    driver.implicitly_wait(10000)
    count = count.text.replace(',', '')
    count = int(count)
    driver.implicitly_wait(1)
    pages = ceil(count / 20)

    df = pd.DataFrame()
    all_tables = pd.read_html(driver.page_source, attrs={'id': 'bfi-table'})
    df = pd.concat([df, all_tables[0]], axis=0)
    print(df.shape)

    for i in range(pages - 2):
        button = driver.find_element(by=By.ID, value='bfi-table_next')
        driver.execute_script("arguments[0].click();", button)

        driver.implicitly_wait(1)
        all_tables = pd.read_html(driver.page_source, attrs={'id': 'bfi-table'})
        df = pd.concat([df, all_tables[0]], axis=0)
        print(df.shape)

    filename = CATEGORY.lower().replace(' ', '_')
    df.to_csv(f'results/{filename}.csv', index=False)
    print(df.shape)
    # element = driver.find_element_by_css('div[class*="loadingWhiteBox"]')
    # driver.execute_script("arguments[0].click();", element)
    #
    # element = driver.find_element_by_css('div[class*="loadingWhiteBox"]')
    # webdriver.ActionChains(driver).move_to_element(element).click(element).perform()


    # details = '/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[1]/a[1]'


    driver.quit()


if __name__ == "__main__":
    main_parser()
