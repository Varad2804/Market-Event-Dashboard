from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os

OUTPUT_CSV = "rights_issues_latest.csv"
EXPECTED_HEADERS = [
    "Company Name", "Record Date", "Issue Open", "Renunciation of Rights Entitlements",
    "Issue Close", "Issue price (Per Share)", "Issue Size (Rs Cr)", 
    "CMP of Share", "CMP of Rights Entitlement", "Rights Issue Ratio"
]


driver=webdriver.Chrome()
driver.get("https://www.chittorgarh.com/report/latest-rights-issue-in-india/75/")

try:
    WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.TAG_NAME,'table')))

    tables = driver.find_elements(By.TAG_NAME, "table")
    df_target=None

    for table in tables:
        rows=table.find_elements(By.TAG_NAME,"tr")
        if not rows:
            continue
        headers = [th.text.strip().split('\n')[0] for th in rows[0].find_elements(By.TAG_NAME, "th")]
        # print(headers)
        if all(h in headers for h in EXPECTED_HEADERS[:5]):  # Loose match
            data = []
            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if not cols:
                    continue
                row_data = [col.text.strip() for col in cols]
                data.append(row_data)

            df_target = pd.DataFrame(data, columns=headers)
            break  # Stop after finding the correct table
    
    if os.path.exists(OUTPUT_CSV):
            df_old = pd.read_csv(OUTPUT_CSV)
            df_merged = df_target.merge(df_old, how='outer', indicator=True)
            df_diff = df_merged[df_merged['_merge'] == 'left_only'].drop(columns=['_merge'])

            if not df_diff.empty:
                print("🆕 New entries found:")
                print(df_diff)
            else:
                print("✅ No new entries.")
    else:
        print("📁 No previous CSV found. Saving initial version...")

        # Save latest data
        df_target.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Data saved to {OUTPUT_CSV}")

finally:
    driver.quit()