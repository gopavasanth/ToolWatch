import os
from flask import Flask, render_template
import requests
from model import Session, Tool, Base, engine
from urllib.parse import urlparse 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tools.db'

@app.route('/')
def index():
    session = Session()
    tools = session.query(Tool).all()
    was_crawled = []
    for tool in tools:
        url_parsed = urlparse(tool.url)
        if url_parsed.hostname != None and 'toolforge.org' in url_parsed.hostname :
            was_crawled.append(True)
        else:
            was_crawled.append(False)
    return render_template('index.html', tools=tools, was_crawled=was_crawled)

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
