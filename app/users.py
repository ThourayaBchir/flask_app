from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from .database import mongo
from flask import redirect, url_for, request
from flask_login import UserMixin
from app import login
from bson import ObjectId

db = mongo.db

@login.user_loader
def load_user(id):
    return User.get(User, id)


class User(UserMixin):
    def __init__(self, username, id):
        self.id = id
        self.username = username
        self.email = None
        self.password_hash = None

    def register(self, username, password):
        return

    def login(self):
        username = request.args['username']
        password_hash = generate_password_hash(request.args['password'])
        user = db.users.find_one({'username': username, 'password_hash': password_hash})
        if user is None:
            return redirect(url_for('register'))
        return redirect(url_for('index'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get(self, id):
        user = db.users.find_one({'_id': ObjectId(id)})
        return User(user['username'], user['_id'])

    def find(self, username):
        return db.users.find_one({'username': username})

    def get_user(self, username, password):
        user_doc = mongo.db.users.find_one({'username': username})
        if user_doc is None or not check_password_hash(user_doc.get('password_hash'), password): # hash
            return None
        return User(username, str(user_doc['_id']))

    def verify_username(self, username):
        return db.users.find_one({'username': username})

    def verify_email(self, email):
        return db.users.find_one({'email': email})

    def insert_new_user(self, username, email, password):
        password_hash = generate_password_hash(password)
        return mongo.db.users.insert_one({'username': username, 'password_hash': password_hash, 'email': email})

    def get_by_username(self, username):
        user_doc = mongo.db.users.find_one({'username': username})
        return User(username, str(user_doc['_id']))

    def log_filename(self, username, filename):
        user_data = dict(mongo.db.users.find_one({'username': username}))
        if 'filename' in user_data.keys():
            user_data['filename'].append(filename)
        else:
            user_data['filename'] = [filename]
        mongo.db.users.update({'_id': user_data['_id']}, user_data, upsert=True)
        return

    def get_uploaded_files(self, username):
        user_data = dict(mongo.db.users.find_one({'username': username}))
        if 'filename' in user_data.keys():
            return user_data['filename']
        else:
            return None
