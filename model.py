from sqlalchemy import create_engine, Column, Integer, Boolean, TIMESTAMP, Text, String, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, mapped_column, scoped_session
from sqlalchemy import ForeignKey

import datetime
from config import config

engine = create_engine(config["MARIADB_URI"])
Session = scoped_session(sessionmaker(bind=engine))  # Scoped session per request
Base = declarative_base()  # Use declarative_base from sqlalchemy.orm

# Association table for the M2M relationship between Tool and Maintainer
tool_maintainers = Table(
    "tool_maintainers",
    Base.metadata,
    Column("tool_id", Integer, ForeignKey("tools.id"), primary_key=True),
    Column("maintainer_id", Integer, ForeignKey("maintainers.id"), primary_key=True),
)


class Tool(Base):
    __tablename__ = "tools"
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
    maintainers = relationship("Maintainer", secondary=tool_maintainers, back_populates="tools")
    records = relationship("Record", back_populates="tool")
    tool_preferences = relationship("ToolPreferences", back_populates="tool")


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True)
    tool_id = mapped_column(ForeignKey("tools.id"))
    timestamp = Column(TIMESTAMP, default=datetime.datetime.now)
    health_status = Column(Boolean, default=False)
    tool = relationship("Tool", back_populates="records")


class Maintainer(Base):
    __tablename__ = "maintainers"
    id = Column(Integer, primary_key=True)
    username = Column(String(500), unique=True, nullable=False)
    tools = relationship("Tool", secondary=tool_maintainers, back_populates="maintainers")
    tool_preferences = relationship("ToolPreferences", back_populates="")


class ToolPreferences(Base):
    __tablename__ = "tool_preferences"
    id = Column(Integer, primary_key=True)
    interval = Column(Integer, default=0)
    send_email = Column(Boolean, default=True)
    user = relationship("Maintainer", back_populates="tool_preferences")
    tool = relationship("Tool", back_populates="tool_preferences")
    tool_id = mapped_column(ForeignKey("tools.id"))
    user_id = mapped_column(ForeignKey("maintainers.id"))
