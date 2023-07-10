import requests
from flask import render_template, request
from tools import app
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

        # Create a ThreadPoolExecutor to perform health checks concurrently
        with ThreadPoolExecutor() as executor:
            futures = []

            # Schedule health check for each tool
            for tool_data in tools_data:
                tool = {
                    "name": tool_data["name"],
                    "url": f"https://{tool_data['name']}.toolforge.org/",
                    "health_status": "Loading...",
                    "last_checked": None
                }
                tools.append(tool)

                # Schedule health check for the current tool
                future = executor.submit(check_tool_health, tool["url"])
                futures.append((tool, future))

            # Retrieve the health check results
            for tool, future in futures:
                tool["health_status"] = future.result()

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
    return render_template('index.html', tools=tools, current_page=page)
