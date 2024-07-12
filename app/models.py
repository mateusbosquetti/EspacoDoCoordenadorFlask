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

class Setor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=False)
    setor = db.relationship('Setor', back_populates='professores')

Setor.professores = db.relationship('Professor', order_by=Professor.id, back_populates='setor')

class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    materia = db.Column(db.String, nullable=False)
    sala = db.Column(db.String, nullable=False)
    dia = db.Column(db.String, nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    professor = db.relationship('Professor', back_populates='aulas')

Professor.aulas = db.relationship('Aula', order_by=Aula.id, back_populates='professor')
