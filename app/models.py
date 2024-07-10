from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)

class Contato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turma = db.Column(db.String, nullable=True)
    nome = db.Column(db.String, nullable=True)

class Atividade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomeAtv  = db.Column(db.String, nullable=True)
    descricao  = db.Column(db.String, nullable=True)

class Suporte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    mensagem = db.Column(db.String, nullable=True)
