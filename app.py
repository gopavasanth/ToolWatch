from flask import Flask, render_template
import requests
from sqlalchemy import create_engine, Column, String, Integer, Boolean, TIMESTAMP 
from sqlalchemy.orm import sessionmaker, declarative_base  # Import declarative_base from sqlalchemy.orm
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tools.db'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
Base = declarative_base()  # Use declarative_base from sqlalchemy.orm

class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String)
    description = Column(String)
    url = Column(String)
    keywords = Column(String)
    author = Column(String)
    repository = Column(String)
    license = Column(String)
    technology_used = Column(String)
    bugtracker_url = Column(String)
    health_status = Column(Boolean, default=False)
    last_checked = Column(TIMESTAMP, default=datetime.datetime.now)

@app.route('/')
def index():
    session = Session()
    tools = session.query(Tool).all()
    return render_template('index.html', tools=tools)

def fetch_and_store_data():
    API_URL = "https://toolsadmin.wikimedia.org/tools/toolinfo/v1.2/toolinfo.json"
    response = requests.get(API_URL)
    data = response.json()

    session = Session()
    for tool_data in data:
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
            bugtracker_url=tool_data.get('bugtracker_url', '')  # Use .get() to handle missing keys
        )

        isExisting = session.query(Tool).filter_by(name=tool.name).first()
        if not isExisting:
            session.add(tool)
        else:
            # delete the existing tool and add the new one
            session.delete(isExisting)
            session.add(tool)
    session.commit()


scheduler = BackgroundScheduler()
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
    Base.metadata.create_all(engine)
    fetch_and_store_data()
    scheduler.add_job(fetch_and_store_data, 'interval', hours=1)
    scheduler = Scheduler()
    scheduler.add_job(id='Scheduled task', func=ping_every_30_minutes, trigger='interval', minutes=30)
    scheduler.start()
    app.run(debug=True)
