from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def get_market_cap(company="Dam Capital"):
    driver=webdriver.Chrome()
    driver.get("https://www.bseindia.com/markets/equity/EQReports/allindiamktcap.aspx")


    try:
        WebDriverWait(driver,10).until(
            EC.presence_of_all_elements_located((By.ID,"getquotesearch"))
        )

        search_box=driver.find_element(By.ID,"getquotesearch")
        search_box.send_keys(company)

        # Wait for the dropdown to populate
        time.sleep(2)  # simpler than waiting for dropdown entry

        # Click the first item in the dropdown
        first_result = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ulSearchQuote li")))
        first_result.click()
        
        mcap_element = WebDriverWait(driver,1).until(EC.presence_of_element_located(
            (By.XPATH, "//td[text()='Mcap Full (Cr.)']/following-sibling::td")
        ))

        print("Market Cap Full (Cr.):", mcap_element.text)
        return mcap_element.text


    finally:
        driver.quit()


if __name__=="__main__":
    get_market_cap()