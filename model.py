from sqlalchemy import create_engine, Column, Integer, Boolean, TIMESTAMP, Text
from sqlalchemy.orm import sessionmaker, declarative_base  # Import declarative_base from sqlalchemy.orm
import datetime
from config import config

engine = create_engine(config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
Base = declarative_base()  # Use declarative_base from sqlalchemy.orm

class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    title = Column(Text)
    description = Column(Text)
    url = Column(Text)
    keywords = Column(Text)
    author = Column(Text)
    repository = Column(Text)
    license = Column(Text)
    technology_used = Column(Text)
    bugtracker_url = Column(Text)
    health_status = Column(Boolean, default=False)
    last_checked = Column(TIMESTAMP, default=datetime.datetime.now)
    page_num = Column(Integer)
    total_pages = Column(Integer)