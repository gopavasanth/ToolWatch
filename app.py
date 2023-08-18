from flask import Flask, render_template,request
import requests
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base  # Import declarative_base from sqlalchemy.orm

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
    page_num = Column(Integer)
    total_pages = Column(Integer)

@app.route('/')
def index():
    session = Session()
    curr_page = int(request.args.get("page",1))
    tools = session.query(Tool).filter(Tool.page_num == curr_page).all()
    if not tools:
        tools = session.query(Tool).filter(Tool.page_num == 1).all()
        curr_page = 1
    return render_template('index.html',tools=tools,curr_page=curr_page,total_pages=tools[0].total_pages)

@app.route('/search')
def search():
    session = Session()
    search_term = request.args.get("search","")
    query = search_term.split(":")
    if len(query) != 2:
        return render_template('index.html',tools=[],search_term=search_term,curr_page=1,total_pages=1)
    key,value = query
    if key in ["name","title","author"]:
        tools = session.query(Tool).filter(getattr(Tool,key.lower()).ilike(f"%{value}%")).all()
    else:
        tools = session.query(Tool).filter(Tool.keywords.contains(value)).all()
    return render_template('index.html',tools=tools,search_term=search_term,curr_page=1,total_pages=1)

def fetch_and_store_data():
    API_URL = "https://toolsadmin.wikimedia.org/tools/toolinfo/v1.2/toolinfo.json"
    response = requests.get(API_URL)
    data = response.json()
    session = Session()
    page_limit = 50
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

if __name__ == '__main__':
    print("Fetching and storing data...")
    Base.metadata.create_all(engine)
    fetch_and_store_data()
    print("Starting server on port 5000...")
    app.run(debug=True)
