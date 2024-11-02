import os
import requests
import datetime
import time
from flask import Flask
from model import db, Tool, Record
from config import config
from urllib.parse import urlparse

page_limit = config['page_limit']

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config["MARIADB_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def fetch_and_store_data():
    API_URL = config['API_URL']
    # Example implementation of fetching and storing data
    response = requests.get(API_URL)
    
    tools_data = response.json()
    # print(tools_data)

    for tool_data in tools_data:
        tool = Tool(
            name=tool_data.get("name", ""),
            title=tool_data.get("title", ""),
            description=tool_data.get("description", ""),
            url=tool_data.get("url", ""),
            keywords=tool_data.get("keywords", ""),
            author=tool_data.get("author", ""),
            repository=tool_data.get("repository", ""),
            license=tool_data.get("license", ""),
            technology_used=tool_data.get("technology_used", ""),
            bugtracker_url=tool_data.get("bugtracker_url", ""),
            health_status=tool_data.get("health_status", False),
            last_checked=datetime.datetime.now(),
            page_num=tool_data.get("page_num", 1),
            total_pages=tool_data.get("total_pages", 1)
        )
        db.session.add(tool)
    db.session.commit()

def sync_get(url):
    response = requests.get(url)
    return response.json()

def ping_every_30_minutes():
    while True:
        tools = Tool.query.all()
        for tool in tools:
            response = requests.get(tool.url)
            tool.health_status = response.status_code == 200
            tool.last_checked = datetime.datetime.now()
            db.session.commit()
        time.sleep(1800)