
from flask import Flask, request,  send_from_directory, jsonify, make_response
from flask_cors import CORS
from cryptocode import encrypt, decrypt
import os
import time
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

UPLOAD_FOLDER = '/Users/vlad/Desktop/Main/Projects/AnonyGram/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, template_folder='templates')
CORS(app)
app.config['SECRET_KEY'] = 'fJjfKDSJfsKIOEOIRUEKODCMKsvmgfdjfkDSJHBgijJKHSDJGfjJHSFIGjkdjhFHIdhjshjkIFEHUiuwiqeoipreopwkodmvMK'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:4253@localhost/anonygram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,  db)

key = 'fJjfKDSJfsKIOEOIRUEKODCMKsvmgfdjfkDSJHBgijJKHSDJGfjJHSFIGjkdjhFHIdhjshjkIFEHUiuwiqeoipreopwkodmvMK'

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
    icon = db.Column(db.String(100), nullable=True)
    
    __table_args__ = tuple((
        db.PrimaryKeyConstraint('id', name='user_pk'),
        db.UniqueConstraint('username'),
        db.UniqueConstraint('email')
    ))
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User id={self.id} name={self.name} username={self.username} icon={self.icon}>'

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    message = db.Column(db.String, default='')
    file = db.Column(db.String, nullable=True)
    chat_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    created_on = db.Column(db.Integer, default=time.time(), nullable=False)
    
    __table_args__ = tuple((
        db.ForeignKeyConstraint(['user_id'], ['users.id']),
        db.ForeignKeyConstraint(['chat_id'], ['chats.id'])
    ))
    
    def __repr__(self):
        return f'<Message id={self.id} message_text={self.message} file={self.file} created_on={self.created_on}>'

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String, default='')
    admins = db.relationship("User", secondary=chat_admin, back_populates="admins")
    users = db.relationship("User", secondary=user_chat, back_populates="chats")
    messages = db.relationship("Message", order_by=Message.id)
    icon = db.Column(db.String(100), nullable=True)
    
    __table_args__ = tuple((
        db.PrimaryKeyConstraint('id', name='chat_pk')
    ))
    
    def __repr__(self):
        return f'<Chat id={self.id} name={self.name} icon={self.icon}>'

def login():
    email = request.form.get('email')
    password = request.form.get('password')
    hash = request.form.get('hash')
    
    result = db.session.execute(db.select(User).where(User.email == email))
    user = result.scalar()
    if not user:
        return (False, make_response(jsonify({'status': 'NOTOK', 'message': 'Log in failed. Invalid email.', 'data': {}}), 200))
    elif (not user.check_password(password) and not hash) or (not user.password == password and hash):
        return (False, make_response(jsonify({'status': 'NOTOK', 'message': 'Log in failed. Invalid password.', 'data': {}}), 200))
    return (True, user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# User
@app.route('/api/set_name/', methods=['POST'])
def set_name():
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    user.name = request.form.get('name')
    db.session.commit()
    return make_response(jsonify({'status': 'OK', 'message': 'Name changed.', 'data': {'new_name': user.name}}), 200)

# TODO: Add to docs
@app.route('/api/set_icon/', methods=['POST'])
def set_icon():
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    user.icon = request.form.get('file')
    db.session.commit()
    return make_response(jsonify({'status': 'OK', 'message': 'Icon of user changed.', 'data': {'new_icon': user.icon}}), 200)

# TODO: Add to docs
@app.route('/api/user_info/', methods=['POST'])
def user_info():
    result = login()
    if result[0]:
        pass
    else:
        return result[1]
    
    result = db.session.execute(db.select(User).where(User.id == request.form.get('user_id')))
    user = result.scalar()
    
    return make_response(jsonify({'status': 'OK', 'message': 'User data sended.', 'data': {'name': user.name, 'icon': user.icon, 'id': user.id}}), 200)


# Chat
@app.route('/api/create_chat/', methods=['POST'])
def create_chat():
    chat_name = request.form.get('chat_name')
    
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    chat = Chat(name=chat_name)
    chat.admins.append(user)
    chat.users.append(user)
    db.session.add(chat)
    db.session.commit()
    return make_response(jsonify({'status': 'OK', 'message': 'Chat created.', 'data': {}}), 200)

# TODO: Add to docs
@app.route('/api/set_chat_icon/', methods=['POST'])
def set_chat_icon():
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    result = db.session.execute(db.select(Chat).where(Chat.id == request.form.get('chat_id')))
    chat = result.scalar()
    chat.icon = request.form.get('file')
    db.session.commit()
    return make_response(jsonify({'status': 'OK', 'message': 'Icon of chat changed.', 'data': {'new_icon': chat.icon}}), 200)

# TODO: Add to docs
@app.route('/api/add_user_to_chat/', methods=['POST'])
def add_user_to_chat():
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    result = db.session.execute(db.select(Chat).where(Chat.id == request.form.get('chat_id')))
    chat = result.scalar()
    if user in chat.users:
        result = db.session.execute(db.select(User).where(User.id == request.form.get('user_id')))
        user = result.scalar()
        chat.users.append(user)
        db.session.commit()
        return make_response(jsonify({'status': 'OK', 'message': 'User added to chat.', 'data': {'new_user': user.id}}), 200)
    else:
        return make_response(jsonify({'status': 'OK', 'message': 'You dont in this chat.', 'data': {}}), 200)

# TODO: Add to docs
@app.route('/api/add_admin_to_chat/', methods=['POST'])
def add_admin_to_chat():
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    result = db.session.execute(db.select(Chat).where(Chat.id == request.form.get('chat_id')))
    chat = result.scalar()
    if user in chat.admins:
        result = db.session.execute(db.select(User).where(User.id == request.form.get('user_id')))
        user = result.scalar()
        chat.admins.append(user)
        db.session.commit()
        return make_response(jsonify({'status': 'OK', 'message': 'Admin added to chat.', 'data': {'new_user': user.id}}), 200)
    else:
        return make_response(jsonify({'status': 'OK', 'message': 'You dont admin in this chat.', 'data': {}}), 200)

@app.route('/api/chat_info/', methods=['POST'])
def chat_info():
    chat_id = request.form.get('chat_id')
    
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    result = db.session.execute(db.select(Chat).where(Chat.id == chat_id))
    chat = result.scalar()
    
    ids = []
    for user in chat.users:
        ids.append(user.id)
        
    admin_ids = []
    for user in chat.users:
        admin_ids.append(user.id)
    
    return make_response(jsonify({'status': 'OK', 'message': 'Chat info sended.', 'data': {'users': ids, 'admins': admin_ids, 'name': chat.name, 'icon': chat.icon}}), 200)

@app.route('/api/chat_messages/', methods=['POST'])
def chat_messages():
    chat_id = request.form.get('chat_id')
    
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    result = db.session.execute(db.select(Chat).where(Chat.id == chat_id))
    chat = result.scalar()
    
    messages = []
    for message in chat.messages:
        messages.append([decrypt(message.message, key), message.file, message.user_id, message.created_on])
    
    return make_response(jsonify({'status': 'OK', 'message': 'Chat messages sended.', 'data': {'messages': messages}}), 200)

@app.route('/api/chat_list/', methods=['POST'])
def chat_list():
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    ids = []
    for chat in user.chats:
        ids.append(chat.id)
    
    return make_response(jsonify({'status': 'OK', 'message': 'Chat list sended.', 'data': ids}), 200)


# Messages
@app.route('/api/send_message/', methods=['POST'])
def send_message():
    email = request.form.get('email')
    message_text = request.form.get('message')
    chat_id = request.form.get('chat_id')
    file = request.form.get('file')
    
    result = login()
    if result[0]:
        user = result[1]
    else:
        return result[1]
    
    result = db.session.execute(db.select(Chat).where(Chat.id == chat_id))
    chat = result.scalar()
    if file is None:
        message = Message(message=encrypt(message_text, key), user_id=user.id, chat_id=chat_id, created_on=time.time())
    else:
        message = Message(message=encrypt(message_text, key), user_id=user.id, chat_id=chat_id, created_on=time.time(), file=file)
    db.session.add(message)
    db.session.commit()
    return make_response(jsonify({'status': 'OK', 'message': 'Message sended.', 'data': {'message_text': message_text, 'email': email}}), 200)


# Uploads
@app.route('/api/upload_file/', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return make_response(jsonify({'status': 'OK', 'message': 'File uploaded.', 'data': {'file_path': os.path.join(app.config['UPLOAD_FOLDER'], file.filename)}}), 200)
    
@app.route('/api/uploads/<string:filename>/', methods=['POST', 'GET'])
def uploaded_files(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except:
        return make_response('File not founded', 404)


# Registration and login
@app.route('/api/login/', methods=['POST'])
def api_login():
    result = login()
    if result[0]:
        user = result[1]
        return make_response(jsonify({'status': 'OK', 'message': 'Log in successful.', 'data': {'email': request.form.get('email'), 'password_hash': user.password, 'id': user.id}}), 200)
    else:
        return result[1]

@app.route('/api/register/', methods=['POST'])
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
    return make_response(jsonify({'status': 'OK', 'message': 'Registration successful.', 'data': {'username': username, 'email': email, 'password_hash': user.password, 'id': user.id}}), 200)


if __name__ == '__main__':
    db.create_all()
    app.run()
