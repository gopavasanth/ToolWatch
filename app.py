import json
from urllib.parse import urlparse

from flask import Flask, abort, render_template, request
from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound

from config import config
from model import Base, Record, Session, Tool, engine
from utils import fetch_and_store_data

app = Flask(__name__)
app.config["MARIADB_URI"] = config["MARIADB_URI"]
page_limit = config["page_limit"]


@app.route("/")
def index():
    session = Session()
    curr_page = int(request.args.get("page", 1))
    tools = session.query(Tool).all()
    paginated_tools = tools[(curr_page - 1) * page_limit : curr_page * page_limit]

    was_crawled = []
    for tool in paginated_tools:
        url_parsed = urlparse(tool.url)
        if url_parsed.hostname != None and "toolforge.org" in url_parsed.hostname:
            was_crawled.append(True)
        else:
            was_crawled.append(False)
    return render_template(
        "index.html",
        tools=paginated_tools,
        was_crawled=was_crawled,
        curr_page=curr_page,
        total_pages=tools[0].total_pages,
    )


@app.route("/search")
def search():
    session = Session()
    search_term = request.args.get("search", "")
    tools = session.query(Tool).all()
    filtered_tools = []
    for tool in tools:
        if (
            search_term.lower() in tool.url.lower()
            or search_term.lower() in tool.title.lower()
            or search_term.lower() in tool.author.lower()
        ):
            filtered_tools.append(tool)
    was_crawled = []
    for tool in filtered_tools:
        url_parsed = urlparse(tool.url)
        if url_parsed.hostname != None and "toolforge.org" in url_parsed.hostname:
            was_crawled.append(True)
        else:
            was_crawled.append(False)
    return render_template(
        "index.html",
        tools=filtered_tools,
        search_term=search_term,
        curr_page=1,
        total_pages=1,
        was_crawled=was_crawled,
    )


@app.route("/tools/<int:id>")
def show_details(id):
    session = Session()
    try:
        tool = session.get(Tool, id)
        records = (
            session.query(Record)
            .filter(Record.tool_id == id)
            .order_by(desc(Record.timestamp))
            .all()
        )
        health_statuses = [record.health_status for record in records]
        days = [record.timestamp.strftime("%d %b") for record in records]
        return render_template(
            "details.html",
            tool=tool,
            health_statuses=json.dumps(health_statuses),
            days=json.dumps(days),
        )

    except NoResultFound as e:
        abort(404)


if __name__ == "__main__":
    print("Running Development Server...")
    Base.metadata.create_all(engine)
    session = Session()
    if session.query(Tool).count() == 0:
        # if db is empty, fetch data
        print("Fetching and storing data...")
        fetch_and_store_data()
    print("Starting Flask server at 5000...")

    app.run(debug=True)
