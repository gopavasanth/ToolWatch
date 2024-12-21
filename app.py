import os
import json
from datetime import datetime
from urllib.parse import urlparse
import re
from authlib.integrations.flask_client import OAuth

from flask import Flask, render_template, request, redirect, session as flask_session
from sqlalchemy import extract

from config import config
from model import Base, Record, Session, Tool, engine, Tool_preferences
from utils import fetch_and_store_data

app = Flask(__name__)
app.config["SECRET_KEY"] = config["SECRET"]
app.config["MARIADB_URI"] = config["MARIADB_URI"]
app.config["SESSION_COOKIE_SECURE"] = True if "MODE" in os.environ else False
app.config["SESSION_COOKIE_HTTPONLY"] = True
page_limit = config["page_limit"]

oauth = OAuth(app)
oauth.register(
    name="toolwatch",
    client_id=config["CLIENT_ID"],
    client_secret=config["CLIENT_SECRET"],
    access_token_url="https://meta.wikimedia.org/w/rest.php/oauth2/access_token",
    access_token_params=None,
    authorize_url="https://meta.wikimedia.org/w/rest.php/oauth2/authorize",
    authorize_params=None,
    api_base_url="https://meta.wikimedia.org/w/rest.php/oauth2",
)
tool = oauth.create_client("toolwatch")


@app.route("/login")
def login():
    toolwatch = oauth.create_client("toolwatch")
    return toolwatch.authorize_redirect()


@app.route("/logout")
def logout():
    flask_session.pop("user")
    return redirect("/")


@app.route("/api/auth/mediawiki/callback")
def authorize():
    oauth.toolwatch.authorize_access_token()
    profile_resp = oauth.toolwatch.get("oauth2/resource/profile")
    profile_resp.raise_for_status()
    profile = profile_resp.json()

    flask_session["user"] = {"username": profile["username"]}

    return redirect("/")


@app.route("/")
def index():
    session = Session()
    curr_page = int(request.args.get("page", 1))
    sort_by = request.args.get("sort_by", "title")
    order = request.args.get("order", "asc")

    # Fetch all tools from the database, excluding the ones that are not web tools
    tools = session.query(Tool).filter(Tool.web_tool == True).all()

    # Sorting tools by title after normalizing (removing non-alphanumeric characters from the start and stripping spaces)
    if sort_by == "title":
        tools = sorted(
            tools,
            key=lambda x: re.sub(r"^\W+", "", x.title.strip().lower()),
            reverse=(order == "desc"),
        )

    # Pagination logic
    paginated_tools = tools[(curr_page - 1) * page_limit : curr_page * page_limit]

    # Calculate health stats
    total_tools = len(tools)
    tools_up = sum(1 for tool in tools if tool.health_status)
    tools_down = total_tools - tools_up

    # Identify which tools were crawled
    was_crawled = []
    for tool in paginated_tools:
        url_parsed = urlparse(tool.url)
        was_crawled.append(bool(url_parsed.hostname and "toolforge.org" in url_parsed.hostname))

    return render_template(
        "index.html",
        tools=paginated_tools,
        was_crawled=was_crawled,
        curr_page=curr_page,
        total_pages=(total_tools // page_limit) + 1,
        tools_up=tools_up,
        tools_down=tools_down,
        total_tools=total_tools,
        sort_by=sort_by,
        order=order,
    )


@app.route("/search")
def search():
    session = Session()
    search_term = request.args.get("search", "")
    tools = session.query(Tool).all()

    # Filter tools by search term in URL, title, author, or description
    filtered_tools = []
    for tool in tools:
        if (
            search_term.lower() in tool.url.lower()
            or search_term.lower() in tool.title.lower()
            or search_term.lower() in tool.author.lower()
            or search_term.lower() in tool.description.lower()
        ):
            filtered_tools.append(tool)

    # Check if the tool was crawled (has a toolforge.org hostname)
    was_crawled = []
    for tool in filtered_tools:
        url_parsed = urlparse(tool.url)
        if url_parsed.hostname is not None and "toolforge.org" in url_parsed.hostname:
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


@app.route("/tools/<int:id>", methods=["GET", "POST"])
def show_details(id):
    month = request.form.get("month") if request.form else datetime.now().month
    year = request.form.get("year") if request.form else datetime.now().year

    session = Session()
    tool = session.get(Tool, id)
    records = (
        session.query(Record)
        .filter(Record.tool_id == id)
        .order_by(Record.timestamp)
        .filter(extract("year", Record.timestamp) == year)
        .filter(extract("month", Record.timestamp) == month)
    )

    health_statuses = [record.health_status for record in records]
    days = [record.timestamp.strftime("%d %b") for record in records]
    return render_template(
        "details.html",
        tool=tool,
        health_statuses=json.dumps(health_statuses),
        days=json.dumps(days),
        selected_year=year,
        selected_month=month,
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    session = Session()

    if request.method == "POST":
        for downtime in request.form.keys():
            tool_pref = session.query(Tool_preferences).get(downtime.split("__")[1])
            print(downtime.split("__")[1])
            print(request.form[downtime])
            tool_pref.interval = request.form[downtime]
        session.commit()

    tool_prefs = (
        session.query(Tool_preferences).filter(Tool_preferences.user_name == flask_session["user"]["username"]).all()
    )
    return render_template("profile.html", tool_prefs=tool_prefs)


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
