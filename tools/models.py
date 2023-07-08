from tools import db
from datetime import datetime

# Define the Tool model
class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tool {self.name}>'
