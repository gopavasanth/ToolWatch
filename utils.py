import os
import requests
import datetime
import time
from model import Session, Tool, Base, engine, Record, Tool_preferences, User
from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse

page_limit = config['page_limit']

def fetch_and_store_data():
    API_URL = config['API_URL']
    response = requests.get(API_URL)
    data = response.json()
    session = Session()
    total_pages = len(data) // page_limit
    for page in range(1, total_pages + 1):
        start = (page - 1) * page_limit
        end = page * page_limit
        page_data = data[start:end]

        for tool_data in page_data:
            if session.query(Tool).filter(Tool.name == tool_data['name']).count() > 0:
                tool = session.query(Tool).filter(Tool.name == tool_data['name']).first()
                tool.web_tool = tool_data.get('tool_type') == 'web app'
                session.commit()
                continue
            tool = Tool(
                name=tool_data['name'],
                title=tool_data['title'],
                description=tool_data['description'],
                url=tool_data['url'],
                keywords=tool_data.get('keywords', ''),  # Use .get() to handle missing keys
                author=tool_data['author'][0]['name'],
                repository=tool_data.get('repository', ''),  # Use .get() to handle missing keys
                license=tool_data.get('license', ''),  # Use .get() to handle missing keys
                technology_used=', '.join(tool_data.get('technology_used', [])),  # Use .get() to handle missing keys
                bugtracker_url=tool_data.get('bugtracker_url', ''),  # Use .get() to handle missing keys
                page_num = page,
                total_pages = total_pages,
                web_tool = tool_data.get('tool_type') == 'web app'
            )
            session.add(tool)
    session.commit()

def sync_get(url):
    try:
        print( f'[*] Fetching url {url}' )
        response = requests.head(url, timeout=5)
        if response.status_code >= 200 and response.status_code < 399:
            return True
        else:
            return False
    except requests.RequestException:
        return False

def ping_every_30_minutes():
    engine = create_engine(config['MARIADB_URI'])
    SessionInit = sessionmaker(bind=engine)
    session = SessionInit()
    # Fetch all tools from the database, excluding the ones that are not web tools
    tools = session.query(Tool).filter(Tool.web_tool == True).all()
    print("Checking health status of tools")
    for tool in tools:
        url = tool.url
        time.sleep(0.01)
        url_parsed = urlparse(url)
        print( f'[*] Checking health of {url} with hostname {url_parsed.hostname}' )
        if  url_parsed.hostname != None and 'toolforge.org' in url_parsed.hostname:
            result = sync_get(url)
        else:
            result = False # Don't check the health of non-toolforge.org urls
        print(f'[*] {url} is {result}')
        tool.health_status = result
        tool.last_checked = datetime.datetime.now()
        record = Record(tool=tool, health_status=result)
        session.add(tool)
        session.add(record)
        session.commit()
