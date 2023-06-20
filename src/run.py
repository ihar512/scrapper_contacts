from logging import exception
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd
import os


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
    service_section = {'Lighting_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td[1]/input',
                       'Sound_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td[1]',
                       'Staging / Rigging_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[4]/td[1]/input',
                       'Video & Projection_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[5]/td[1]/input',
                       'Set / Scenic Design and Construction_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[6]/td[1]/input',
                       'Manufacturers / Distributors_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[7]/td[1]/input',
                       'Lasers_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[8]/td[1]/input',
                       'Fog and Haze Machines_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[9]/td[1]/input',
                       'Cases_XPath': '/html/body/table/tbody/tr[3]/td[2]/table[1]/tbody/tr[2]/td[1]/form/table/tbody/tr[1]/td[1]/table/tbody/tr[12]/td[1]/input'}
    url = URL_BASE
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(2)
    try:
        for service in service_section.values():
            print(service)
            elements = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, service)))
            elements.click()
    except NoSuchElementException as error:
        logger.info("cannot find checkbox: %s", error)
        driver.quit()
    
    try:    
        # go to home search page, click submit
        elements = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "submit")))
        logger.info("submit button found")
        elements.click()
    except NoSuchElementException as error:
        logger.info("cannot find submit button: %s", error)
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


def save_to_file(df_input: pd.DataFrame):
    filename = os.path.basename(__file__)
    filepath = os.path.realpath(__file__)
    filepath_result = filepath.replace('\src\\' + filename, '\companies_info.csv')
    df_input.to_csv(filepath_result, index=False, header=True, mode="w")


def drop_company_duplicates():
    filename = os.path.basename(__file__)
    filepath = os.path.realpath(__file__)
    filepath_input = filepath.replace('\src\\' + filename, '\companies_info.csv')
    df_duplicates = pd.read_csv(filepath_input)
    df_filtered = df_duplicates.drop_duplicates(subset=['COMPANY_NAME', 'WEBSITE'])
    print(df_filtered)
    filepath_result = filepath.replace('\src\\' + filename, '\companies_info_filtered.csv')
    df_filtered.to_csv(filepath_result, index=False, header=True, mode="w")


def main():
    df_companies_info = get_company_sites()
    save_to_file(df_companies_info)
    drop_company_duplicates()


if __name__ == "__main__":
    main()
