from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tool(db.Model):
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    url = db.Column(db.Text)
    keywords = db.Column(db.Text)
    author = db.Column(db.Text)
    repository = db.Column(db.Text)
    license = db.Column(db.Text)
    technology_used = db.Column(db.Text)
    bugtracker_url = db.Column(db.Text)
    health_status = db.Column(db.Boolean, default=False)
    last_checked = db.Column(db.TIMESTAMP, default=datetime.now)
    page_num = db.Column(db.Integer)
    total_pages = db.Column(db.Integer)
    
    # Relationship to Record model
    records = db.relationship("Record", back_populates="tool")

class Record(db.Model):
    __tablename__ = 'records'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("tools.id"))
    timestamp = db.Column(db.TIMESTAMP, default=datetime.now)
    health_status = db.Column(db.Boolean, default=False)
    
    # Relationship to Tool model
    tool = db.relationship("Tool", back_populates="records")

