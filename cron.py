import requests
import datetime
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Tool,Base,engine,Session
from urllib.parse import urlparse
from config import config
from utils import ping_every_30_minutes,fetch_and_store_data


if __name__ == '__main__':
    print("Running Production Server...")
    Base.metadata.create_all(engine)
    session = Session()
    print("Fetching and storing data...")
    fetch_and_store_data()
    ping_every_30_minutes()