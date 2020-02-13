import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    API_TOKEN = os.environ.get('API_TOKEN')
