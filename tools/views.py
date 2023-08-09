import requests
from flask import render_template, request
from tools import app, db
from tools.models import Tool
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def fetch_tools(page, limit):
    url = "https://hay.toolforge.org/directory/api.php"
    params = {
        "page": page,
        "limit": limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        tools_data = response.json()
        tools = []

        for tool_data in tools_data:
            tool = Tool.query.filter_by(name=tool_data["name"]).first()
            if tool:
                # Update existing tool with latest data
                tool.url = f"http://{tool_data['name']}.toolforge.org/"
                tool.last_checked = datetime.utcnow()
                tools.append(tool)
            else:
                # Create a new tool in the database
                new_tool = Tool(
                    name=tool_data["name"],
                    url=f"http://{tool_data['name']}.toolforge.org/",
                    last_checked=datetime.utcnow()
                )
                tools.append(new_tool)
                db.session.add(new_tool)

        # Commit the changes to the database
        db.session.commit()

        return tools
    else:
        return []


def check_tool_health(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    limit = 50
    tools = fetch_tools(page, limit)

    # Perform health check for each tool using multithreading
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(check_tool_health, tool.url): tool for tool in tools}

        for future in concurrent.futures.as_completed(futures):
            tool = futures[future]
            tool.health_status = future.result()
            tool.last_checked = datetime.utcnow()

    # Commit the changes to the database
    db.session.commit()

    return render_template('index.html', tools=tools, current_page=page)
