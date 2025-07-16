from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time

def get_buybacks():
    OUTPUT_CSV = "Buy_Backs.csv"
    EXPECTED_HEADERS = [
        "Company Name", "Record Date", "Issue Open", "Issue Close", "Buyback Type",
        "Buyback price (Per Share)", "Current Market Price", 
        "Issue Size - Shares (Cr)", "Issue Size - Amount (Cr)"
    ]

    # ✅ Headless config for FastAPI/server use
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.chittorgarh.com/report/latest-buyback-issues-in-india/80/?year=2025#table_section")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        tables = driver.find_elements(By.TAG_NAME, 'table')
        df_target = None

        for table in tables:
            rows = table.find_elements(By.TAG_NAME, 'tr')
            if not rows:
                continue
            headers = [th.text.strip().split('\n')[0] for th in rows[0].find_elements(By.TAG_NAME, "th")]
            if all(h in headers for h in EXPECTED_HEADERS[:5]):
                data = []
                for row in rows[1:]:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if not cols:
                        continue
                    row_data = [col.text.strip() for col in cols]
                    data.append(row_data)

                df_target = pd.DataFrame(data, columns=headers)
                break

        if df_target is not None:
            # Save the latest data
            df_target.to_csv(OUTPUT_CSV, index=False)
            return df_target.to_dict(orient="records")
        else:
            return {"error": "❌ Buyback table not found or failed to load."}

    finally:
        driver.quit()

if __name__=="__main__":
    get_buybacks()