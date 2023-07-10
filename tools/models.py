from tools import db
from datetime import datetime

# Define the Tool model
class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(200))
    health_status = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tool {self.name}>'
