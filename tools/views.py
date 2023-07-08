import requests
from flask import render_template, request
from tools import app


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
            tool = {
                "name": tool_data["name"],
                "url": f"http://{tool_data['name']}.toolforge.org/",
                "health_status": "Loading...",
                "last_checked": None
            }
            tools.append(tool)
        return tools
    else:
        return []


def check_tool_health(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(url, 'Healthy')
            return 'Healthy'
        else:
            print(url, 'Unhealthy')
            return 'Unhealthy'
    except requests.exceptions.RequestException:
        return 'Error'


@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    limit = 50
    tools = fetch_tools(page, limit)
    # for tool in tools:
        # tool["health_status"] = check_tool_health(tool["url"])
    return render_template('index.html', tools=tools, current_page=page)
