from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time

def get_rights_issues():
    OUTPUT_CSV = "rights_issues_latest.csv"
    EXPECTED_HEADERS = [
        "Company Name", "Record Date", "Issue Open", "Renunciation of Rights Entitlements",
        "Issue Close", "Issue price (Per Share)", "Issue Size (Rs Cr)", 
        "CMP of Share", "CMP of Rights Entitlement", "Rights Issue Ratio"
    ]

    # 👉 Not using headless, so we can see the browser
    options = webdriver.ChromeOptions()
    # Comment out or remove these to run with UI
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.chittorgarh.com/report/latest-rights-issue-in-india/75/")

    try:
        # Optional: scroll to bottom to trigger table load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # wait for JS to load table

        tables = driver.find_elements(By.TAG_NAME, "table")
        df_target = None

        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            if not rows:
                continue
            headers = [th.text.strip().split('\n')[0] for th in rows[0].find_elements(By.TAG_NAME, "th")]
            if all(h in headers for h in EXPECTED_HEADERS[:5]):  # Loose match
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
            print("✅ Data scraped successfully")
            print(df_target.head())
            return df_target.to_dict(orient="records")
        else:
            print("❌ Table not found")
            return {"error": "Table not found"}

    finally:
        driver.quit()

if __name__ == "__main__":
    get_rights_issues()
