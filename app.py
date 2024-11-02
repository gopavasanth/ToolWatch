# app.py
import json
from datetime import datetime
from urllib.parse import urlparse
import re

from flask import Flask, abort, render_template, request
from sqlalchemy import extract
from flask_migrate import Migrate

from config import config
from model import db, Record, Tool
from utils import fetch_and_store_data

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config["MARIADB_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

page_limit = config["page_limit"]

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def index():
    curr_page = int(request.args.get("page", 1))
    sort_by = request.args.get("sort_by", "title")
    order = request.args.get("order", "asc")

    # Sort and paginate tools
    query = Tool.query
    if sort_by == "title":
        query = query.order_by(Tool.title.asc() if order == "asc" else Tool.title.desc())
    tools_paginated = query.paginate(page=curr_page, per_page=page_limit)

    # Calculate health stats
    total_tools = Tool.query.count()
    tools_up = Tool.query.filter_by(health_status=True).count()
    tools_down = total_tools - tools_up

    # Identify which tools were crawled
    was_crawled = [
        bool(urlparse(tool.url).hostname and "toolforge.org" in urlparse(tool.url).hostname)
        for tool in tools_paginated.items
    ]

    return render_template(
        "index.html",
        tools=tools_paginated.items,
        was_crawled=was_crawled,
        curr_page=curr_page,
        total_pages=tools_paginated.pages,
        tools_up=tools_up,
        tools_down=tools_down,
        total_tools=total_tools,
        sort_by=sort_by,
        order=order,
    )

@app.route("/search")
def search():
    search_term = request.args.get("search", "")
    tools = Tool.query.filter(
        (Tool.url.ilike(f"%{search_term}%")) |
        (Tool.title.ilike(f"%{search_term}%")) |
        (Tool.author.ilike(f"%{search_term}%")) |
        (Tool.description.ilike(f"%{search_term}%"))
    ).all()

    # Check if each tool was crawled (has a toolforge.org hostname)
    was_crawled = [
        bool(urlparse(tool.url).hostname and "toolforge.org" in urlparse(tool.url).hostname)
        for tool in tools
    ]

    return render_template(
        "index.html",
        tools=tools,
        search_term=search_term,
        curr_page=1,
        total_pages=1,
        was_crawled=was_crawled,
    )

@app.route("/tools/<int:id>", methods=["GET", "POST"])
def show_details(id):
    month = int(request.form.get("month", datetime.now().month))
    year = int(request.form.get("year", datetime.now().year))

    tool = Tool.query.get_or_404(id)
    records = Record.query.filter(
        Record.tool_id == id,
        extract("year", Record.timestamp) == year,
        extract("month", Record.timestamp) == month
    ).order_by(Record.timestamp).all()

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

if __name__ == "__main__":
    print("Running Development Server...")

    # Create tables and fetch data if necessary
    with app.app_context():
        if Tool.query.count() == 0:
            print("Fetching and storing data...")
            fetch_and_store_data()

    app.run(debug=True)
