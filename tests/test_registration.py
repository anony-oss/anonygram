import os
from ..server.extensions import start_extensions, db
from ..server.views import *
from ..server.app import app
import json
from faker import Faker
from faker.providers import person, internet, misc

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(misc)

class TestRegistration():
    def setup_method(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join('/Users/vlad/Desktop/Main/Projects/AnonyGram/', 'test.db')
        app.config['SECRET_KEY'] = 'testing'
        app.config['TESTING'] = True
    
        start_extensions(app)
        db.drop_all(app=app)
        db.create_all(app=app)
        self.app = app.test_client()
    
    def test_registration(self):
        username = fake.first_name()
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password))
        data = req.get_data(as_text=True) 
        assert 'Registration successful.' in data 
        assert username in data
        assert email in data
        
    def test_registration_error_email(self):
        username = fake.first_name()
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password))
        data = req.get_data(as_text=True) 
        
        username_2 = fake.first_name()
        password_2 = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username_2, email=email, password=password_2))
        data = req.get_data(as_text=True) 
        
        assert 'Registration failed. Username or email already in use.' in data
        
    def test_registration_error_username(self):
        username = fake.first_name()
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password))
        data = req.get_data(as_text=True) 
        
        email_2 = fake.email()
        password_2 = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email_2, password=password_2))
        data = req.get_data(as_text=True) 
        
        assert 'Registration failed. Username or email already in use.' in data
        
    def test_registration_error_both(self):
        username = fake.first_name()
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password))
        data = req.get_data(as_text=True) 
        
        password_2 = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password_2))
        data = req.get_data(as_text=True) 
        
        assert 'Registration failed. Username or email already in use.' in data
        
    def test_registration_invalid_post(self):   
        req = self.app.post('/api/register/')
        data = req.get_data(as_text=True) 
        assert 'Registration failed. Invalid post data.' in data
        
    def test_login_password(self):
        username = fake.first_name()
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password))
        data = json.loads(req.get_data(as_text=True))
        hs = data['data']['password_hash']
        id = str(data['data']['id'])
        
        req = self.app.post('/api/login/', data=dict(email=email, password=password))
        data = req.get_data(as_text=True)
        assert 'Log in successful.' in data
        assert email in data
        assert hs in data
        assert id in data
        
    def test_login_hash(self):
        username = fake.first_name()
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password))
        data = json.loads(req.get_data(as_text=True))
        hs = data['data']['password_hash']
        id = str(data['data']['id'])
        
        req = self.app.post('/api/login/', data=dict(email=email, password=hs))
        data = req.get_data(as_text=True)
        assert 'Log in successful.' in data
        assert email in data
        assert hs in data
        assert id in data
        
    def test_login_invalid_email(self):
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/login/', data=dict(email=email, password=password))
        data = req.get_data(as_text=True)
        assert 'Log in failed. Invalid email.' in data
        
    def test_login_invalid_password(self):
        username = fake.first_name()
        email = fake.email()
        password = fake.password()
        
        req = self.app.post('/api/register/', data=dict(username=username, email=email, password=password))
        
        password = fake.password()
        
        req = self.app.post('/api/login/', data=dict(email=email, password=password))
        data = req.get_data(as_text=True)
        assert 'Log in failed. Invalid password.' in data
        
    def test_login_invalid_post(self):
        req = self.app.post('/api/login/')
        data = req.get_data(as_text=True)
        assert 'Log in failed. Invalid post data.' in data