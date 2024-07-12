from app import app, db
from flask import render_template, url_for, request, redirect, flash
from app.forms import AtividadeForm, ContatoForm, UserForm, LoginForm
from app.models import Atividade, Setor, User, Suporte
from flask_login import login_user, logout_user, current_user
import requests

@app.route('/', methods=['GET','POST'])
def homepage():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
    return render_template('index.html', form = form)

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = UserForm()
    if form.validate_on_submit():
        user = form.save()
        login_user(user, remember=True)
        return redirect(url_for('homepage'))
    return render_template('cadastro.html', form=form)

@app.route('/sair/')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/contato/', methods=['GET', 'POST'])
def contato():
    form = ContatoForm()
    context = {}
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('homepage'))
    return render_template('contatos.html', context=context, form=form)

@app.route('/contato/lista/')
def contatoLista():
    if request.method == 'GET':
        pesquisa = request.args.get('pesquisa', '')
    dados  = Setor.query.order_by('nome')
    if pesquisa != '':
        dados = dados.filter_by(nome=pesquisa)
    context = {'dados': dados.all()}
    return render_template('contato_lista.html', context=context)

@app.route('/contato/<int:id>')
def contatoDetail(id):
    obj = Setor.query.get(id)
    return render_template('contato_detail.html', obj=obj)

@app.route('/atividade/', methods=['GET', 'POST'])
def atividade():
    form = AtividadeForm()
    context = {}
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('homepage'))
    return render_template('atividade.html', context=context, form=form)

@app.route('/atividade/lista/')
def atividadeLista():
    if request.method == 'GET':
        pesquisa = request.args.get('pesquisa', '')
    dados  = Atividade.query.order_by('nomeAtv')
    if pesquisa != '':
        dados = dados.filter_by(nome=pesquisa)
    context = {'dados': dados.all()}
    return render_template('atividade_lista.html', context=context)

@app.route('/suporte', methods=['GET', 'POST'])
def suporte():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        mensagem = request.form['message']

        novo_suporte = Suporte(nome=nome, email=email, mensagem=mensagem)
        db.session.add(novo_suporte)
        db.session.commit()

        # Envio de e-mail usando StaticForms
        staticforms_url = "https://api.staticforms.xyz/submit"
        data = {
            "accessKey": "c9e5c3a3-07ee-4249-8818-e89aab33b38f",
            "name": nome,
            "email": email,
            "message": mensagem,
            "redirectTo": url_for('suporte', _external=True)
        }
        
        response = requests.post(staticforms_url, data=data)
        
        if response.status_code == 200:
            flash('Sua mensagem foi enviada com sucesso!', 'success')
        else:
            flash('Ocorreu um erro ao enviar a mensagem. Tente novamente.', 'error')

        return redirect(url_for('suporte'))

    return render_template('suporte.html')

@app.route('/delete_setor/<int:id>', methods=['POST'])
def delete_setor(id):
    setor = Setor.query.get_or_404(id)
    db.session.delete(setor)
    db.session.commit()
    return redirect(url_for('homepage'))

@app.route('/edit_setor/<int:id>', methods=['GET', 'POST'])
def edit_setor(id):
    setor = Setor.query.get_or_404(id)
    if request.method == 'POST':
        setor.nome = request.form['nome']
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template('edit_setor.html', setor=setor)
