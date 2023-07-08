import os

FLASK_APP="OSM",
FLASK_DEBUG=True,
SECRET_KEY="toolwatch",
TEMPLATES_AUTO_RELOAD=True,
SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'tools.db')