import os
from dotenv import load_dotenv
load_dotenv()


curr_env = os.environ['ENV'] if 'ENV' in os.environ else 'development'
DB_URL = "tools.db.svc.wikimedia.cloud" if curr_env == 'production' else "localhost"
DB_USERNAME = os.getenv('DB_USERNAME') if curr_env == 'production' else "root"
DB_PASSWORD = os.getenv('DB_PASSWORD') if curr_env == 'production' else "toolwatch"
DB_NAME = os.getenv('DB_NAME') if curr_env == 'production' else "toolwatch"

config = {
    'MARIADB_URI': f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_URL}:3306/{DB_NAME}',
    'page_limit': 25,
    'API_URL': "https://toolsadmin.wikimedia.org/tools/toolinfo/v1.2/toolinfo.json"
}
