from logging import exception
import requests
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd
import os
import subprocess


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s %(module)s:%(lineno)d][%(levelname)s] - %(message)s",
                    handlers=[logging.FileHandler("logfile.log"), logging.StreamHandler()])
# logging.basicConfig(level=logging.INFO,
#                     format="[%(asctime)s %(module)s:%(lineno)d][%(levelname)s] - %(message)s",
#                     filename='logfile.log',
#                     filemode='w')


def get_company_sites() -> pd.DataFrame:
    URL_BASE = "https://www.epdweb.com/search.php"
    service_section = {'Lighting': '9'}
    url = URL_BASE + "?section=" + service_section["Lighting"]
    driver = webdriver.Firefox()
    driver.get(url)
    try:
        # go to home search page, click submit
        elements = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "submit")))
        logger.info("submit button found")
        elements.click()
    except NoSuchElementException:
        logger.info("cannot find submit button")
        driver.quit()

    try:
    # find last page number
        XPATH_LAST_PAGE_BUTTON = "/html/body/table/tbody/tr[3]/td[2]/div[4]/table/tbody/tr[1]/td[3]/small/a"
        elements = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, XPATH_LAST_PAGE_BUTTON)))
        link_last_page = elements.get_attribute("href")
        print(link_last_page)
        tokens = link_last_page.split("page=")
        base_page_url = tokens[0]
        last_page_num = tokens[1]
        logger.info("found last page button and number")
    except NoSuchElementException:
        logger.info("cannot find last page element")
        driver.quit()
    
    # iterate through each page, then add company pages to list
    company_page_list=[]
    for page in range(2,int(last_page_num)+1):
        try:
            XPATH_TABLE_COMPANIES = "//div[contains(@class,'directory-listing')]//table[contains(@class,'inside')]//a[contains(@class,'tablesubhead')]"
            elements = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, XPATH_TABLE_COMPANIES)))
            company_all = driver.find_elements(By.XPATH, XPATH_TABLE_COMPANIES)
        except NoSuchElementException:
            logger.info("no table of company elements found")
            driver.quit()
        for company in company_all:
            link = company.get_attribute('href')
            company_page_list.append(link)
        logger.info("company's pages href saved from page {} of table of companies".format(page-1))
        driver.get(base_page_url + "page=" + str(page))

    # get each company website url
    OUTPUT_COL_NAMES = ['COMPANY_NAME','SERVICE_SECTION','WEBSITE']
    df_companies_info = pd.DataFrame(columns=OUTPUT_COL_NAMES)
    for page in company_page_list:
        XPATH_COMPANY_TITLE = "/html/body/table/tbody/tr[3]/td[2]/div[2]"
        XPATH_WEBSITE_COMPANY = "/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr/td[1]/table/tbody/tr[2]/td[1]/table/tbody/tr/td/div[1]/a[2]"
        try:
            driver.get(page)
            elements = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_WEBSITE_COMPANY)))
            name = driver.find_element(By.XPATH, XPATH_COMPANY_TITLE)
            name_extract = name.text.split('- ')[0].strip('"')
            service = name.text.split('- ')[1].strip()
            site = driver.find_element(By.XPATH, XPATH_WEBSITE_COMPANY)
            df_new_row = pd.DataFrame(data=[[name_extract, service, site.text]], columns=OUTPUT_COL_NAMES)
            df_companies_info = pd.concat([df_companies_info, df_new_row], ignore_index=True)
            logger.info("Added new company info to table, new company name is {}".format(name_extract))
        except (TimeoutException, NoSuchElementException) as ex:
            logger.info("Skip extracting company info from {}/n{}".format(page, ex))
    return df_companies_info

    # headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    # URL = "https://www.epdweb.com/search_result.php"
    # r = requests.get(URL,
    #                  headers=headers,
    #                  params={'section': '9', 'page': '1'})
    # print(r.content)
    # soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup.prettify())
    # results = soup.find_all("div", class_="directory-listing")
    # print(results)


def save_to_file(df_input: pd.DataFrame):
    filename = os.path.basename(__file__)
    filepath = os.path.realpath(__file__)
    filepath_result = filepath.replace('\src\\' + filename, '\companies_info.csv')
    df_input.to_csv(filepath_result, index=False, header=True, mode="w")


def run_thescrapper():
    return


def get_contact_from_url():
    current_path = os.path.abspath(__file__)
    print(current_path)
    tokens = current_path.split('src')
    filepath = tokens[0] + 'companies_info.csv'
    try:
        df = pd.read_csv(filepath)
        print(df)
    except Exception as error:
        logger.info(error)
    return
    

def main():
    # df_companies_info = get_company_sites()
    # save_to_file(df_companies_info)
    # go through the list of urls
    get_contact_from_url()
    

if __name__ == "__main__":
    main()