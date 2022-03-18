from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

cors: CORS = CORS()
db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

def start_extensions(app):
    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)