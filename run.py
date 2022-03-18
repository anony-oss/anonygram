from project.views import *
from project.app import db, app
    
db.create_all(app=app)
app.run()