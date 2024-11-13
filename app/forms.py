from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app import db, bcrypt
from app.models import DEFAULT_PROFILE_PICTURE_URL, Setor, User


class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(),Email()]) 
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confimar senha', validators=[DataRequired()])
    adm = False
    profile_picture=DEFAULT_PROFILE_PICTURE_URL
    btnSubmit = SubmitField('Cadastrar')


    def save(self):
        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))
        user = User(
            nome = self.nome.data,
            email = self.email.data,
            senha = senha,
            adm = self.adm,
            profile_picture = self.profile_picture
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

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Login')
        

class ProfessorForm(FlaskForm):
    usuario = SelectField('Selecione o Professor', coerce=int)
    btnSubmit = SubmitField('Adicionar Professor')