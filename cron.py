import asyncio
import requests
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Tool

def sync_get(url):
    try:
        print( f'[*] Fetching url {url}' )
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False

async def aysnc_ping_every_30_minutes():
    engine = create_engine('sqlite:///tools.db')
    SessionInit = sessionmaker(bind=engine)
    session = SessionInit()
    tools = session.query(Tool).all()
    urls = []
    print("Checking health status of tools")
    for t in tools:
        urls.append(t.url)
    print('Gathered urls')
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(None, sync_get, url) for url in urls]
    print(f'Gathering results for {len(futures)} urls')
    results = await asyncio.gather(*futures)
    print('Gathered results')
    for tool in tools:
        result = results.pop(0)
        tool.health_status = result
        tool.last_checked = datetime.datetime.now()
        session.add(tool)
    session.commit()

def ping_every_30_minutes():
    asyncio.run(aysnc_ping_every_30_minutes())

if __name__ == '__main__':
    ping_every_30_minutes()