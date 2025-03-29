from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import configure_mappers
from flask import session
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
import models
from models import User, Admin

login_manager = LoginManager(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type') 

    if user_type == 'user':
        return User.query.get(int(user_id))
    elif user_type == 'admin':
        return Admin.query.get(int(user_id))

    return None
    

import routes
configure_mappers()
import forms
