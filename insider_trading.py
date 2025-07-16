from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from MarketCapfetcher import get_market_cap  # Your existing market cap scraper
import time

def get_insider_trading():
    headers = [
        "Security Code", "Security Name", "Name of Person", "Category of Person",
        "Securities held pre Transaction",
        "Type of Securities", "Number", "Value", "Transaction Type",
        "Securities held post Transaction",
        "Period",
        "Mode of Acquisition",
        "Type of Contract", "Buy Value (Units~)", "Sale Value (Units~)",
        "Reported to Exchange"
    ]

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # comment this out if debugging
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.bseindia.com/corporates/Insider_Trading_new.aspx")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
        )

        tables = driver.find_elements(By.TAG_NAME, "table")
        if len(tables) < 3:
            return {"error": "❌ Table structure has changed on BSE site"}

        rows = tables[2].find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows[2:]:  # Skip headers
            cols = row.find_elements(By.TAG_NAME, "td")
            cols = [col.text.strip() for col in cols]
            if cols:
                data.append(cols)

        df = pd.DataFrame(data, columns=headers)
        df.to_csv("insider_trading_data.csv", index=False)

        insider_trades = []
        for index, row in df.iterrows():
            company = ' '.join(row['Security Name'].split())
            trade_value = row['Value']
            person = row['Name of Person']

            try:
                # clean up and convert to float
                market_capital = get_market_cap(company).replace(",", "").strip()
                trade_value_clean = trade_value.replace(",", "").strip()

                trade_value_float = float(trade_value_clean) / 1e7  # Rs to Cr
                market_cap_float = float(market_capital)

                impact = (trade_value_float / market_cap_float) * 100

                if impact >= 1.0:
                    insider_trades.append({
                        "Company": company,
                        "Person": person,
                        "Trade Value (Rs)": trade_value,
                        "Market Cap (Cr)": market_capital,
                        "Impact %": f"{impact:.2f}"
                    })
            except Exception as e:
                print(f"❌ Error processing {company}: {e}")
                continue

        return insider_trades

    finally:
        driver.quit()

if __name__=="__main__":
    trades=get_insider_trading()
    print(trades)
