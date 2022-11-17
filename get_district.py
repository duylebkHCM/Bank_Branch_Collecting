from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import re
import os
import pandas as pd
import re
import glob

DRIVE_PATH = 'chromedriver'

def collect_data(src, browser: Chrome):
    df = pd.read_csv(os.path.join(src, os.path.basename(src) + '_prov.csv'))
    
    for prov_idx in range(len(df)):
        prov_dir = os.path.join(src, df.loc[prov_idx, df.columns[0]])
        if not os.path.exists(prov_dir):
            os.makedirs(prov_dir, exist_ok=True)

        prov_url = df.loc[prov_idx, df.columns[1]]
        browser.get(prov_url) 

        district_name_pttn = re.compile(r'<a.*>([\-\.\d\w\s]+)\(\d+\)</a>')

        detail_tab = browser.find_element(By.XPATH, '//*[@id="main"]/div[2]/div[5]/div[1]/ul')

        childs = detail_tab.find_elements(By.XPATH, '//*[@id="main"]/div[2]/div[5]/div[1]/ul/li')
        distri = []
        dis_url = []

        child: WebElement
        for dis_idx, child in enumerate(childs):
            item = child.find_element(By.XPATH, f'//*[@id="main"]/div[2]/div[5]/div[1]/ul/li[{dis_idx+1}]/a')
            url = item.get_attribute('href')
            outerHTML = item.get_attribute('outerHTML')
            matcher = re.match(district_name_pttn, outerHTML)
            if matcher:
                name = matcher.group(1)
            else:
                print(outerHTML)

            distri.append(name)
            dis_url.append(url)
            
        bank_level3 = pd.DataFrame({'distri_name': distri, 'dis_urls' : dis_url})
        bank_level3.to_csv(os.path.join(prov_dir, f'{df.loc[prov_idx, df.columns[0]]}_dis.csv'), index=False, header=True)

        browser.execute_script("window.open('');")

if __name__ == '__main__':
    opts = Options()
    bank_lst = glob.glob('data/*')

    for d_ in bank_lst:
        browser = Chrome(executable_path=DRIVE_PATH)
        print('Collect', d_)
        collect_data(src=d_, browser=browser)
        browser.close()
        print('Reinitialize driver')