from .server.views import *
from .server.app import db, app

db.create_all(app=app)
app.run()