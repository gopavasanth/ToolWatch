from sqlalchemy import create_engine, Column, String, Integer, Boolean, TIMESTAMP 
from sqlalchemy.orm import sessionmaker, declarative_base  # Import declarative_base from sqlalchemy.orm
import datetime

engine = create_engine('sqlite:///tools.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()  # Use declarative_base from sqlalchemy.orm

class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String)
    description = Column(String)
    url = Column(String)
    keywords = Column(String)
    author = Column(String)
    repository = Column(String)
    license = Column(String)
    technology_used = Column(String)
    bugtracker_url = Column(String)
    health_status = Column(Boolean, default=False)
    last_checked = Column(TIMESTAMP, default=datetime.datetime.now)
    page_num = Column(Integer)
    total_pages = Column(Integer)