import os
from flask import Flask, render_template,request
import requests
from model import Session, Tool, Base, engine
from urllib.parse import urlparse
from config import config
from utils import fetch_and_store_data

app = Flask(__name__)
app.config['MARIADB_URI'] = config['MARIADB_URI']
page_limit = config['page_limit']

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

@app.route('/tools/<int:id>')
def get_charts(id):
    try:
        tool = session.query(Tool).filter_by(id=id).first()
        record = session.query(record).filter_by(id=id).first()
        return render_template("graph.html", tool = tool, record = record, isValid = True)
    except EXCEPTION as e: 
        return render_template("graph.html", isValid = False)


if __name__ == '__main__':
    print("Running Development Server...")
    Base.metadata.create_all(engine)
    session = Session()
    if(session.query(Tool).count() == 0):
        # if db is empty, fetch data
        print("Fetching and storing data...")
        fetch_and_store_data()
    print("Starting Flask server at 5000...")
    app.run(debug=True)
