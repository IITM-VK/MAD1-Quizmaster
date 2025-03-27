from dotenv import load_dotenv
from os import getenv
import os

load_dotenv()
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == "True"
SECRET_KEY = os.getenv('SECRET_KEY')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads/profile_pics')
