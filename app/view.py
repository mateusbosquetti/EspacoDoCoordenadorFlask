from app import app, db
from flask import render_template, url_for, request, redirect
from app.forms import AtividadeForm, ContatoForm, UserForm, LoginForm
from app.models import Atividade, Contato, User
from flask_login import login_user, logout_user, current_user


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
    dados  = Contato.query.order_by('nome')
    if pesquisa != '':
        dados = dados.filter_by(nome=pesquisa)
    context = {'dados': dados.all()}
    return render_template('contato_lista.html', context=context)

@app.route('/contato/<int:id>')
def contatoDetail(id):
    obj = Contato.query.get(id)
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

@app.route('/suporte')
def suporte():
    return render_template('suporte.html', current_url=request.url)
