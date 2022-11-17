from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import re
import os
import pandas as pd
import re

DRIVE_PATH = 'chromedriver'

def collect_data(src, browser: Chrome):
    browser.get(src)
    final_name = []
    final_url = []

    table_banks = '//*[@id="tab_supplier"]/ul'
    element = browser.find_element(By.XPATH, table_banks)
    all_children_by_xpath = element.find_elements(By.XPATH, '//*[@id="tab_supplier"]/ul/li')
    print('len(all_children_by_xpath): ' + str(len(all_children_by_xpath)))

    child: WebElement
    for idx, child in enumerate(all_children_by_xpath):
        bank_name = child.find_element(By.XPATH, f'//*[@id="tab_supplier"]/ul/li[{idx + 1}]/a/span')

        outerHTML = bank_name.get_attribute('outerHTML')
        pttn = re.compile(r'<span.*>([\w\s]+)</span>')
        match = re.match(pttn, outerHTML)
        name = match.group(1)

        bank_url = child.find_element(By.XPATH, f'//*[@id="tab_supplier"]/ul/li[{idx+1}]/a')
        href = bank_url.get_attribute('href')

        final_name.append(name)
        final_url.append(href)

    bank_level1 = pd.DataFrame({'name': final_name, 'url': final_url})
    bank_level1.to_csv('bank_level1.csv', index=False, header=True)

    browser.execute_script("window.open('');")

    if not os.path.exists('data'):
        os.mkdir('data')

    for i in range(len(bank_level1)):
        provs = []
        prov_urls = []
        bank_name = bank_level1.loc[i, bank_level1.columns[0]]
        full_bank_name = os.path.join('data', bank_name)
        if not os.path.exists(full_bank_name):
            os.makedirs(full_bank_name, exist_ok=True)

        prov_name_pttn = re.compile(r'<a.*>([\-\w\s]+)\(\d+\)</a>')
        bank_url = bank_level1.loc[i, bank_level1.columns[1]]

        browser.get(bank_url)
        button = browser.find_element(By.ID, 'branch')
        browser.execute_script("arguments[0].click();", button)

        table_prov = browser.find_element(By.XPATH, '//*[@id="page_tb"]/div/div[1]/div/div[2]/div[3]/div[1]/div[4]/div[3]')
        detail_tab = table_prov.find_element(By.XPATH, '//*[@id="page_tb"]/div/div[1]/div/div[2]/div[3]/div[1]/div[4]/div[3]/ul')

        childs = detail_tab.find_elements(By.XPATH, '//*[@id="page_tb"]/div/div[1]/div/div[2]/div[3]/div[1]/div[4]/div[3]/ul/li')

        child: WebElement
        for prov_idx, child in enumerate(childs):
            cols = child.find_elements(By.XPATH, f'//*[@id="page_tb"]/div/div[1]/div/div[2]/div[3]/div[1]/div[4]/div[3]/ul/li[{prov_idx+1}]/a')

            col: WebElement
            for col in cols:
                url = col.get_attribute('href')
                outerHTML = col.get_attribute('outerHTML')
                matcher = re.match(prov_name_pttn, outerHTML)
                if matcher:
                    name = matcher.group(1)
                else:
                    print(outerHTML)
                provs.append(name)
                prov_urls.append(url)
            
        bank_level2 = pd.DataFrame({'prov_name': provs, 'prov_urls' : prov_urls})
        bank_level2.to_csv(os.path.join(full_bank_name, f'{bank_name}_prov.csv'), index=False, header=True)

        browser.execute_script("window.open('');")

if __name__ == '__main__':
    opts = Options()
    browser = Chrome(executable_path=DRIVE_PATH)

    collect_data(src='https://thebank.vn/danh-ba-ngan-hang.html', browser=browser)