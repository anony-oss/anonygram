from flask import Flask
from .extensions import cors, db, migrate, start_extensions
    
def create_app():
    app: Flask = Flask(__name__)
    
    app.config.from_pyfile('config.py')
    
    start_extensions(app)
    return app

app = create_app()