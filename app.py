import os
from flask import Flask, render_template,request
import requests
from model import Session, Tool, Base, engine
from urllib.parse import urlparse 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tools.db'
page_limit = 25

@app.route('/')
def index():
    session = Session()
    curr_page = int(request.args.get("page",1))
    tools = session.query(Tool).all()
    paginated_tools=tools[(curr_page-1)*page_limit:curr_page*page_limit]

    was_crawled = []
    for tool in paginated_tools:
        url_parsed = urlparse(tool.url)
        if url_parsed.hostname != None and 'toolforge.org' in url_parsed.hostname :
            was_crawled.append(True)
        else:
            was_crawled.append(False)
    return render_template('index.html', tools=paginated_tools, was_crawled=was_crawled, curr_page=curr_page,total_pages=tools[0].total_pages)

def fetch_and_store_data():
    API_URL = "https://toolsadmin.wikimedia.org/tools/toolinfo/v1.2/toolinfo.json"
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

@app.route('/search')
def search():
    session = Session()
    search_term = request.args.get("search","")
    tools = session.query(Tool).all()
    filtered_tools = []
    for tool in tools:
        if search_term.lower() in tool.url.lower() or search_term.lower() in tool.title.lower() or search_term.lower() in tool.author.lower():
            filtered_tools.append(tool)
    was_crawled = []
    for tool in filtered_tools:
        url_parsed = urlparse(tool.url)
        if url_parsed.hostname != None and 'toolforge.org' in url_parsed.hostname :
            was_crawled.append(True)
        else:
            was_crawled.append(False)
    return render_template('index.html',tools=filtered_tools,search_term=search_term,curr_page=1,total_pages=1,was_crawled=was_crawled)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = Session()
    if(session.query(Tool).count() == 0):
        print("Fetching and storing data...")
        fetch_and_store_data()
    print("Starting Flask server at 5000...")
    app.run(debug=True)
