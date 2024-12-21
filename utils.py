import os
import requests
import datetime
import time
from model import Session, Tool, Base, engine, Record, Tool_preferences, User
from config import config
from sqlalchemy import create_engine, desc, and_
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
import yagmail

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
            existing_user = session.query(User).filter(User.username == tool_data['author'][0]['name']).first()
            if not existing_user:
                user = User(
                    username = tool_data['author'][0]['name']
                )
                session.add(user)

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

            tool_preferences = Tool_preferences(
                user_name = tool_data['author'][0]['name'],
                tool_id = session.query(Tool).filter(Tool.name == tool_data['name']).first().id
            )
            session.add(tool_preferences)

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

        if(tool.health_status == False):
            down_tool = session.query(Tool_preferences).filter(Tool_preferences.id == tool.id).first()
            last_up = session.query(Record).filter(
                and_(
                    Record.tool_id == tool.id,
                    Record.health_status == True
                )
                ).order_by(desc(Record.timestamp)).first()
            
            if last_up != None:
                #Since the cron job runs every 30 minutes, first time it went down will be 30 minutes + last time it was up.
                if (down_tool.interval*60 >= ((datetime.datetime.now() - last_up.timestamp).total_seconds() + 1800) and down_tool.interval != 0):
                    send_email(down_tool.user_name,down_tool.tool.name)
            



def set_interval(interval,tool):
    session = Session()
    tool = session.query(Tool_preferences).filter(Tool_preferences.tool_id == tool).first()
    tool.interval = interval
    session.commit()

def send_email(username,tool):
    print(f"Sending email to {username}")
    yag = yagmail.SMTP(user='', password='', host='mail.tools.wmcloud.org', port=587)#(email, password)
    yag.send(
        to = '',
        subject="Tool is down",
        contents = "Hi",
    )