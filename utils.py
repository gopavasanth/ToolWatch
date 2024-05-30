import os
import requests
import datetime
import time
from model import Session, Tool, Base, engine, Record
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
                total_pages = total_pages
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
    tools = session.query(Tool).all()
    urls = []
    print("Checking health status of tools")
    for t in tools:
        urls.append(t.url)
    print('Gathered urls')
    results = []
    last_checkeds = []
    for url in urls:
        time.sleep(0.01)
        url_parsed = urlparse(url)
        last_checkeds.append(datetime.datetime.now())
        print( f'[*] Checking health of {url} with hostname {url_parsed.hostname}' )
        if  url_parsed.hostname != None and 'toolforge.org' in url_parsed.hostname:
            result = sync_get(url)
        else:
            result = False # Don't check the health of non-toolforge.org urls
        print(f'[*] {url} is {result}')
        results.append(result)

    print('Gathered results')
    for tool in tools:
        result = results.pop(0)
        tool.health_status = result
        tool.last_checked = last_checkeds.pop(0)
        record = Record(tool=tool, health_status=result)
        session.add(tool)
        session.add(record)
    session.commit()
