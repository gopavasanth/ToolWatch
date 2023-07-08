import requests

API_URL = "https://hay.toolforge.org/directory/api.php"
CHUNK_SIZE = 100  # Number of URLs to process in each chunk


def generate_tool_urls(response):
    tool_urls = []

    for tool_data in response:
        name = tool_data["name"]
        tool_url = f"https://{name}.toolforge.org"
        tool_urls.append(tool_url)

    return tool_urls


def get_tool_data():
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to retrieve tool data.")
        return None


def check_health_status(urls):
    health_status = {}

    for url in urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(url, "Healthy")
                health_status[url] = "Healthy"
            else:
                print(url, "Unhealthy")
                health_status[url] = "Unhealthy"
        except requests.RequestException:
            health_status[url] = "Unreachable"

    return health_status


# Retrieve tool data from the API
tool_data = get_tool_data()

if tool_data:
    # Generate Tool URLs
    urls = [f"https://{tool['name']}.toolforge.org" for tool in tool_data]

    # Divide the URLs into chunks
    url_chunks = [urls[i:i + CHUNK_SIZE] for i in range(0, len(urls), CHUNK_SIZE)]

    # Check health status for each URL chunk
    with open("output.txt", "w", encoding="utf-8") as f:
        for chunk in url_chunks:
            health_status = check_health_status(chunk)
            # Process health status as needed
            for url, status in health_status.items():
                try:
                    print(f"{url} - Status: {status}", file=f)
                except UnicodeEncodeError:
                    print(f"Unable to print URL: {url}", file=f)
else:
    print("No tool data available.")
