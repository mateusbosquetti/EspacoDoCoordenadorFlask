from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app import db, bcrypt
from app.models import Setor, User, Atividade


class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(),Email()]) 
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confimar senha', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Cadastrar')

    def validade_email(self, email):
        if User.query.filter(email=email.data).first():
            return ValidationError('Usuário já cadastradado com esse E-mail!!!')

    def save(self):
        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))
        user = User(
            nome = self.nome.data,
            sobrenome = self.sobrenome.data,
            email = self.email.data,
            senha = senha
        )
        db.session.add(user)
        db.session.commit()
        return user

class SetorForm(FlaskForm):
    nome = StringField('Nome do setor', validators=[DataRequired()])
    
    btnSubmit = SubmitField('Enviar')

    def save(self):
        setor = Setor(
            nome = self.nome.data,
        )   
        db.session.add(setor)
        db.session.commit()

class AtividadeForm(FlaskForm):
    nomeAtv = StringField('Nome da Atividade', validators=[DataRequired()])
    descricao = StringField('Descrição', validators=[DataRequired()])
    
    btnSubmit = SubmitField('Enviar')

    def save(self):
        atividade = Atividade(
            nomeAtv = self.nomeAtv.data,
            descricao = self.descricao.data,
        )
        db.session.add(atividade)
        db.session.commit()

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Login')

    def login(self):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.senha, 
                self.senha.data.encode('utf-8')):
                return user
            else:
                raise Exception('Senha Incorreta!!!')
        else:
            raise Exception('Usuario nao encontrado')