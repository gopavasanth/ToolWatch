import os
from dotenv import load_dotenv

load_dotenv()

curr_env = os.environ["MODE"] if "MODE" in os.environ else "development"
DB_URL = "tools.db.svc.wikimedia.cloud" if curr_env == "production" else "localhost"
DB_USERNAME = os.getenv("TOOL_TOOLSDB_USER") if curr_env == "production" else "root"
DB_PASSWORD = (
    os.getenv("TOOL_TOOLSDB_PASSWORD") if curr_env == "production" else "toolwatch"
)
DB_NAME = f"{DB_USERNAME}__toolwatch" if curr_env == "production" else "toolwatch"

config = {
    "MARIADB_URI": f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_URL}:3306/{DB_NAME}",
    "page_limit": 25,
    "API_URL": "https://toolsadmin.wikimedia.org/tools/toolinfo/v1.2/toolinfo.json",
    "SECRET": os.getenv("SECRET"),
    "CLIENT_ID": os.getenv("OAUTH_CLIENT_ID"),
    "CLIENT_SECRET": os.getenv("OAUTH_CLIENT_SECRET"),
}
