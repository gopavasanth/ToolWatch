# cron.py
import time
import requests
from datetime import datetime

from app import app  # Importing the app from app.py
from model import db, Tool
from utils import fetch_and_store_data

def ping_tools():
    # Create application context
    with app.app_context():
        tools = Tool.query.all()
        print(tools)
        for tool in tools:
            try:
                response = requests.get(tool.url)
                print(f"Pinging {tool.url}...")
                tool.health_status = response.status_code == 200
            except requests.RequestException:
                tool.health_status = False
            tool.last_checked = datetime.now()
            db.session.commit()

if __name__ == "__main__":
    while True:
        print("Pinging tools...")
        fetch_and_store_data()
        ping_tools()
        print("Sleeping for 30 minutes...")
        time.sleep(1800)
