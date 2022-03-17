from app import db
import time
from werkzeug.security import generate_password_hash, check_password_hash

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