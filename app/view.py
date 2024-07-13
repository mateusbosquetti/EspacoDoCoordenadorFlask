from app import app, db
from flask import render_template, url_for, request, redirect, flash
from app.forms import SetorForm, UserForm, LoginForm
from app.models import Setor, User, Suporte, Professor, Aula
from flask_login import login_user, logout_user, current_user
from datetime import time
import requests

@app.route('/home', methods=['GET','POST'])
def homepage():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
        return redirect(url_for('homepage'))
    return render_template('login.html', form=form)

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
    return redirect(url_for('login'))

@app.route('/setor/', methods=['GET', 'POST'])
def setor():
    form = SetorForm()
    context = {}
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('homepage'))
    return render_template('setor/setores.html', context=context, form=form)

@app.route('/setor/lista/')
def setorLista():
    pesquisa = request.args.get('pesquisa', '')
    if pesquisa:
        setores = Setor.query.filter(Setor.nome.ilike(f"%{pesquisa}%")).order_by(Setor.nome).all()
    else:
        setores = Setor.query.order_by(Setor.nome).all()
    return render_template('setor/setor_lista.html', setores=setores)

@app.route('/suporte', methods=['GET', 'POST'])
def suporte():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        mensagem = request.form['message']

        novo_suporte = Suporte(nome=nome, email=email, mensagem=mensagem)
        db.session.add(novo_suporte)
        db.session.commit()

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


@app.route('/setor/<int:setor_id>/professores', methods=['GET', 'POST'])
def manage_professores(setor_id):
    setor = Setor.query.get_or_404(setor_id)
    if request.method == 'POST':
        nome = request.form['nome']
        novo_professor = Professor(nome=nome, setor_id=setor_id)
        db.session.add(novo_professor)
        db.session.commit()
        return redirect(url_for('manage_professores', setor_id=setor_id))
    professores = setor.professores
    return render_template('professor/manage_professores.html', setor=setor, professores=professores)

@app.route('/setor/<int:setor_id>/professor/<int:id>/edit', methods=['GET', 'POST'])
def edit_professor(setor_id, id):
    professor = Professor.query.get_or_404(id)
    if request.method == 'POST':
        professor.nome = request.form['nome']
        db.session.commit()
        return redirect(url_for('manage_professores', setor_id=setor_id))
    return render_template('professor/edit_professor.html', professor=professor)

@app.route('/setor/<int:setor_id>/professor/<int:id>/delete', methods=['POST'])
def delete_professor(setor_id, id):
    professor = Professor.query.get_or_404(id)
    db.session.delete(professor)
    db.session.commit()
    return redirect(url_for('manage_professores', setor_id=setor_id))

@app.route('/setor/<int:id>/delete', methods=['POST'])
def delete_setor(id):
    setor = Setor.query.get_or_404(id)
    if setor.professores:
        return redirect(url_for('confirm_delete_setor', id=id))
    else:
        db.session.delete(setor)
        db.session.commit()
        return redirect(url_for('setorLista'))

@app.route('/setor/<int:id>/confirm_delete', methods=['GET', 'POST'])
def confirm_delete_setor(id):
    setor = Setor.query.get_or_404(id)
    professores = Professor.query.filter_by(setor_id=id).all()
    if request.method == 'POST':
        if 'confirm' in request.form:
            # Deleta todos os professores associados ao setor
            for professor in professores:
                db.session.delete(professor)

            db.session.delete(setor)
            db.session.commit()
            return redirect(url_for('setorLista'))
        return redirect(url_for('setorLista'))
    return render_template('setor/confirm_delete_setor.html', setor=setor, professores=professores)


@app.route('/setor/<int:id>/edit', methods=['GET', 'POST'])
def edit_setor(id):
    setor = Setor.query.get_or_404(id)
    if request.method == 'POST':
        setor.nome = request.form['nome']
        db.session.commit()
        return redirect(url_for('setorLista'))
    return render_template('setor/edit_setor.html', setor=setor)


@app.route('/professor/<int:professor_id>/aulas', methods=['GET', 'POST'])
def manage_aulas(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    if request.method == 'POST':
        materia = request.form['materia']
        sala = request.form['sala']
        dia = request.form['dia']
        horario_inicio = time.fromisoformat(request.form['horario_inicio'])
        horario_fim = time.fromisoformat(request.form['horario_fim'])

        # Verificação de conflito de horário na mesma sala
        conflito = Aula.query.filter(
            Aula.sala == sala,
            Aula.dia == dia,
            Aula.horario_inicio <= horario_fim,
            Aula.horario_fim >= horario_inicio
        ).first()

        if conflito:
            flash('Conflito de horário detectado na sala especificada!', 'error')
        else:
            nova_aula = Aula(
                materia=materia,
                sala=sala,
                dia=dia,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                professor_id=professor_id
            )
            db.session.add(nova_aula)
            db.session.commit()
            flash('Aula adicionada com sucesso!', 'success')
            return redirect(url_for('manage_aulas', professor_id=professor_id))
    
    aulas = professor.aulas
    return render_template('aula/manage_aulas.html', professor=professor, aulas=aulas)


@app.route('/professor/<int:professor_id>/aula/<int:id>/edit', methods=['GET', 'POST'])
def edit_aula(professor_id, id):
    aula = Aula.query.get_or_404(id)
    if request.method == 'POST':
        aula.materia = request.form['materia']
        aula.sala = request.form['sala']
        aula.dia = request.form['dia']
        aula.horario_inicio = time.fromisoformat(request.form['horario_inicio'])
        aula.horario_fim = time.fromisoformat(request.form['horario_fim'])

        # Verificação de conflito de horário na mesma sala
        conflito = Aula.query.filter(
            Aula.id != id,
            Aula.sala == aula.sala,
            Aula.dia == aula.dia,
            Aula.horario_inicio <= aula.horario_fim,
            Aula.horario_fim >= aula.horario_inicio
        ).first()

        if conflito:
            flash('Conflito de horário detectado na sala especificada!', 'error')
        else:
            db.session.commit()
            flash('Aula atualizada com sucesso!', 'success')
            return redirect(url_for('manage_aulas', professor_id=professor_id))
    
    return render_template('aula/edit_aula.html', aula=aula)


@app.route('/professor/<int:professor_id>/aula/<int:id>/delete', methods=['POST'])
def delete_aula(professor_id, id):
    aula = Aula.query.get_or_404(id)
    db.session.delete(aula)
    db.session.commit()
    flash('Aula deletada com sucesso!', 'success')
    return redirect(url_for('manage_aulas', professor_id=professor_id))