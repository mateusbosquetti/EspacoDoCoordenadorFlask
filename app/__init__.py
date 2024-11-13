from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO 

import os
load_dotenv('.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'Login'
bcrypt = Bcrypt(app)
socketio = SocketIO(app)  

from app.view import homepage

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
  cloud_name = "dhfyfwuaf",
  api_key = "525588959485955",
  api_secret = "mmjqRhbyWSVjCxWxvJKFSQYtUlA"
)
