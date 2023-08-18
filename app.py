from flask import Flask, render_template
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
        session.add(tool)
    session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    fetch_and_store_data()
    app.run(debug=True)
