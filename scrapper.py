from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from MarketCapfetcher import get_market_cap
import smtplib
from email.message import EmailMessage

def send_email_alert(subject, html_body, to_emails):
    msg = EmailMessage()
    msg.set_content("This is an HTML email alert")
    msg.add_alternative(html_body, subtype='html')
    msg['Subject'] = subject
    msg['From'] = "your_email@gmail.com"
    msg['To'] = ", ".join(to_emails)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("varadbharadiya@gmail.com", "hyix ijys hpxr ogcu")
        smtp.send_message(msg)

def check_limit_cross(market_cap, trade_value, threshold):
    try:
        # Clean the values
        trade_value = trade_value.replace(',', '').strip()
        market_cap = market_cap.replace(',', '').strip()

        # Convert to float
        trade_value = float(trade_value)
        market_cap = float(market_cap)

        # Convert trade_value from Rs to Cr
        trade_value /= 1e7
        percent_trade = (trade_value / market_cap) * 100

        return {True, percent_trade} if percent_trade >= threshold else {False, percent_trade}
    except Exception as e:
        print(f"❌ Error in check_limit_cross: {e}")
        return {False, 0}


driver = webdriver.Chrome()
driver.get("https://www.bseindia.com/corporates/Insider_Trading_new.aspx")

try:
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
    )
    
    tables = driver.find_elements(By.TAG_NAME, "table")
    target_table = tables[2]

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

    rows = target_table.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in rows[2:]:  # Skip headers
        cols = row.find_elements(By.TAG_NAME, "td")
        cols = [col.text.strip() for col in cols]
        if cols:
            data.append(cols)

    df = pd.DataFrame(data, columns=headers)
    df.to_csv("insider_trading_data.csv", index=True)

    recipients = ["varadbharadiya@gmail.com", "adityajhaver.20@gmail.com", "nshreeinvest@gmail.com"]
    html_alerts = ""
    
    for index, row in df.iterrows():
        company = ' '.join(row['Security Name'].split()[:2])
        trade_value = row['Value']
        person = row['Name of Person']
        
        try:
            market_capital = get_market_cap(company)
            flag, impact = check_limit_cross(market_capital, trade_value, 1)
            if flag:
                html_alerts += f"""
                <hr>
                <b>🚨 Insider Trade Detected</b><br>
                <b>Company:</b> {company}<br>
                <b>Person:</b> {person}<br>
                <b>Trade Value:</b> ₹{trade_value}<br>
                <b>Market Cap:</b> ₹{market_capital}<br>
                <b>Impact:</b> <span style='color:red;'>{impact:.2f}%</span><br>
                """
        except Exception as e:
            print(f"❌ Error processing {company}: {e}")

    if html_alerts:
        # send_email_alert("🚨 Insider Trading Alerts Summary", html_alerts, recipients)
        print("✅ Email alert sent.")
    else:
        print("✅ No significant insider trades found.")

finally:
    driver.quit()
