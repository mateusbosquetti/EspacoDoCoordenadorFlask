from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
import pytz

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

DEFAULT_PROFILE_PICTURE_URL = "https://res.cloudinary.com/dhfyfwuaf/image/upload/v1723118707/z7xfqnj8zlu7ztgfxv5e.jpg"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)
    adm = db.Column(db.Boolean, nullable=True)
    profile_picture = db.Column(db.String, nullable=True, default=DEFAULT_PROFILE_PICTURE_URL)
    
    messages = db.relationship('Message', back_populates='user', cascade='all, delete-orphan')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='messages')

class Suporte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    mensagem = db.Column(db.String, nullable=True)

class Setor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    professores = db.relationship('Professor', back_populates='setor', cascade='all, delete-orphan')

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=False)
    setor = db.relationship('Setor', back_populates='professores')
    aulas = db.relationship('Aula', back_populates='professor', cascade='all, delete-orphan')

class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    materia = db.Column(db.String, nullable=False)
    sala = db.Column(db.String, nullable=False)
    dia = db.Column(db.String, nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    professor = db.relationship('Professor', back_populates='aulas')
