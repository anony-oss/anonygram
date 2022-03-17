from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

UPLOAD_FOLDER = '/Users/vlad/Desktop/Main/Projects/AnonyGram/uploads'

app = Flask(__name__, template_folder='templates')
CORS(app)
app.config['SECRET_KEY'] = 'fJjfKDSJfsKIOEOIRUEKODCMKsvmgfdjfkDSJHBgijJKHSDJGfjJHSFIGjkdjhFHIdhjshjkIFEHUiuwiqeoipreopwkodmvMK'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:4253@localhost/anonygram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,  db)

if __name__ == '__main__':
    from main import *
    db.create_all()
    app.run()