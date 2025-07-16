from fastapi import FastAPI
from Buyback import get_buybacks
from rights_issue import get_rights_issues
from insider_trading import get_insider_trading

app = FastAPI(title="Market Event Tracker API")

@app.get("/")
def index():
    return {"message": "Welcome to the Market Tracker API 🚀"}

@app.get("/buybacks")
def api_buybacks():
    return get_buybacks()

@app.get("/rights-issues")
def api_rights_issues():
    return get_rights_issues()

@app.get("/insider-trading")
def api_insider_trading():
    return get_insider_trading()
