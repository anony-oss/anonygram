from flask import Flask, request, redirect, render_template, send_from_directory, jsonify, make_response
from cryptocode import encrypt, decrypt
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

UPLOAD_FOLDER = '/Users/vlad/Desktop/Main/Projects/AnonyGram/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'fJjfKDSJfsKIOEOIRUEKODCMKsvmgfdjfkDdfgdfgkdjhFHIdhjshjkIFEHUiuwiqeoipreopwkodmvMK'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:4253@localhost/anonygram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,  db)

key = 'fJjfKDSJfsKIOEOIRUEKODCMKsvmkfgopwkodmvMK'

messages = []
names = {}

user_chat = db.Table('userchats', db.Model.metadata, 
    db.Column('user_id', db.Integer(), db.ForeignKey("users.id")),
    db.Column('chat_id', db.Integer(), db.ForeignKey("chats.id"))
)

chat_admin = db.Table('chatadmins', db.Model.metadata, 
    db.Column('chat_id', db.Integer(), db.ForeignKey("chats.id")),
    db.Column('user_id', db.Integer(), db.ForeignKey("users.id"))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)    
    password = db.Column(db.String(200), nullable=True)
    chats = db.relationship(
        "Chat", secondary=user_chat, back_populates="users"
    )
    admins = db.relationship(
        "Chat", secondary=chat_admin, back_populates="admins"
    )
    
    __table_args__ = tuple((
        db.PrimaryKeyConstraint('id', name='user_pk'),
        db.UniqueConstraint('username'),
        db.UniqueConstraint('email')
    ))
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String, default='')
    admins = db.relationship(
        "User", secondary=chat_admin, back_populates="admins"
    )
    users = db.relationship(
        "User", secondary=user_chat, back_populates="chats"
    )
    
    __table_args__ = tuple((
        db.PrimaryKeyConstraint('id', name='chat_pk')
    ))

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    message = db.Column(db.String, default='')
    file = db.Column(db.String, nullable=True)
    chat_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    created_on = db.Column(db.DateTime(), default=datetime.now(), nullable=False)
    
    __table_args__ = tuple((
        db.ForeignKeyConstraint(['user_id'], ['users.id']),
        db.ForeignKeyConstraint(['chat_id'], ['chats.id'])
    ))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/api/set_name/', methods=['POST'])
def set_name():
    name = request.get('data')
    ip = request.remote_addr
    names[ip] = name
    return redirect('/')

@app.route('/api/send_message/', methods=['POST'])
def send_message():
    message = Message(message=encrypt(request.form.get('message'), key))
    db.session.add(message)
    db.session.commit()
    return redirect('/')

@app.route('/api/upload_file/', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return make_response(jsonify({'status': 'OK', 'message': 'File uploaded.', 'data': {'file_path': os.path.join(app.config['UPLOAD_FOLDER'], file.filename)}}), 200)
    
@app.route('/api/uploads/<string:filename>', methods=['POST', 'GET'])
def uploaded_files(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except:
        return make_response('File not founded', 404)

@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    result = db.session.execute(db.select(User).where(User.email == email))
    user = result.scalar()
    if user and user.check_password(password):
        return make_response(jsonify({'status': 'OK', 'message': 'Log in successful.', 'data': {'email': email, 'password_hash': user.password}}), 200)
    else:
        if not user:
            return make_response(jsonify({'status': 'NOTOK', 'message': 'Log in failed. Invalid username.', 'data': {}}), 200)
        else:
            return make_response(jsonify({'status': 'NOTOK', 'message': 'Log in failed. Invalid password.', 'data': {}}), 200)

@app.route('/api/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        return make_response(jsonify({'status': 'NOTOK', 'message': 'Registration failed. Username or email already in use', 'data': {}}), 200)
    return make_response(jsonify({'status': 'OK', 'message': 'Registration successful.', 'data': {'username': username, 'email': email}}), 200)


if __name__ == '__main__':
    db.create_all()
    app.run()
