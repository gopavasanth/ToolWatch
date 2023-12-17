import requests
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Tool
from urllib.parse import urlparse
import time
import datetime
import os


def sync_get(url):
    try:
        print(f"[*] Fetching url {url}")
        response = requests.head(url, timeout=5)
        if response.status_code >= 200 and response.status_code < 399:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def ping_every_30_minutes():
    engine = create_engine("sqlite:///tools.db")
    SessionInit = sessionmaker(bind=engine)
    session = SessionInit()
    if os.path.exists(".venv"):
        print(
            "Running in local envoirnment, limiting health status check upto 10 tools"
        )
        tools = session.query(Tool).limit(10).all()
    else:
        print("Running in production envoirnment, checkig health status for all tools")
        tools = session.query(Tool).all()
    urls = []
    print("Checking health status of tools")
    for t in tools:
        urls.append(t.url)
    print("Gathered urls")
    results = []
    last_checkeds = []
    for url in urls:
        time.sleep(0.01)
        url_parsed = urlparse(url)
        last_checkeds.append(datetime.datetime.now())
        print(f"[*] Checking health of {url} with hostname {url_parsed.hostname}")
        if url_parsed.hostname != None and "toolforge.org" in url_parsed.hostname:
            result = sync_get(url)
        else:
            result = False  # Don't check the health of non-toolforge.org urls
        print(f"[*] {url} is {result}")
        results.append(result)
    print("Gathered results")
    for tool in tools:
        result = results.pop(0)
        tool.health_status = result
        tool.last_checked = last_checkeds.pop(0)
        session.add(tool)
    session.commit()


if __name__ == "__main__":
    ping_every_30_minutes()
