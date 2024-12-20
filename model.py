from sqlalchemy import create_engine, Column, Integer, Boolean, TIMESTAMP, Text
from sqlalchemy.orm import sessionmaker, declarative_base,relationship, mapped_column
from sqlalchemy import ForeignKey

import datetime
from config import config

engine = create_engine(config['MARIADB_URI'])
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
    web_tool = Column(Boolean, default=False)
    health_status = Column(Boolean, default=False)
    last_checked = Column(TIMESTAMP, default=datetime.datetime.now)
    page_num = Column(Integer)
    total_pages = Column(Integer)
    records = relationship("Record", back_populates="tool")

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True)
    tool_id = mapped_column(ForeignKey("tools.id")) 
    tool = relationship("Tool", back_populates="records")
    timestamp = Column(TIMESTAMP, default=datetime.datetime.now)
    health_status = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    email = Column(Text)
    username = Column(Text, primary_key=True)

class Tool_preferences(Base):
    __tablename__ = "tool_preferences"
    id = Column(Integer, primary_key=True)
    user_name = Column(ForeignKey("users.id"))
    tool_id = Column(ForeignKey("tools.id"))