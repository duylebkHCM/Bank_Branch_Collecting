from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import pandas as pd
import glob

DRIVE_PATH = 'chromedriver'

def collect_data(dir_name, src, browser: Chrome):   
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        browser.get(src)

        branch_table = browser.find_element(By.XPATH, '//*[@id="table_branch"]')
        rows = branch_table.find_elements(By.XPATH, '//*[@id="table_branch"]/tbody/tr')

        if len(rows) == 0:
            return

        header = branch_table.find_element(By.XPATH, '//*[@id="table_branch"]/thead')
        header_lst = header.find_elements(By.XPATH, '//*[@id="table_branch"]/thead/tr/th')
        df_cols = [header_lst[1].text, header_lst[2].text]
        
        branch_name = []
        address = []

        for row in rows:
            columns = row.find_elements(By.XPATH,"./td") # Use dot in the xpath to find elements with in element.
            branch_name.append(columns[1].text)
            address.append(columns[2].text)
        
        branch_df = pd.DataFrame({df_cols[0]: branch_name, df_cols[1]: address})
            
        branch_df.to_csv(os.path.join(dir_name, f'{os.path.basename(dir_name)}_branch.csv'), index=False, header=True)

        browser.execute_script("window.open('');")
        # New tabs will be the last object in window_handle

if __name__ == '__main__':
    opts = Options()
    bank_lst = glob.glob('data/*')

    for d_ in bank_lst:
        prov_lst = glob.glob(d_ + '/*')
        new_prov_lst = []
        for prov in prov_lst:
            if os.path.isdir(prov):
                new_prov_lst.append(prov)

        for prov in new_prov_lst:
            distr_df = pd.read_csv(os.path.join(prov, os.path.basename(prov)+'_dis.csv'))
            if len(distr_df) > 0:
                browser = Chrome(executable_path=DRIVE_PATH)
                for idx in range(len(distr_df)):
                    url = distr_df.loc[idx, distr_df.columns[1]]
                    print('Collect', url)
                    dist_name = distr_df.loc[idx, distr_df.columns[0]].strip()
                    dist_name = os.path.join(prov, dist_name)
                    collect_data(dist_name, url, browser)
                browser.close()
                print('Reinitialize driver')
