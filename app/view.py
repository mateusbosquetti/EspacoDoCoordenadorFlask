from app import app, db
from flask import render_template, url_for, request, redirect, flash, send_file
from app.forms import SetorForm, UserForm, LoginForm, ProfessorForm
from app.models import Setor, User, Suporte, Professor, Aula, Chat, Message
from flask_login import login_user, logout_user, current_user
from datetime import time
from io import BytesIO
import pandas as pd
import requests

@app.route('/home', methods=['GET','POST'])
def homepage():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = form.login()
            login_user(user, remember=True)
            return redirect(url_for('homepage'))
        except Exception as e:
            flash(str(e), 'error')
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
        return redirect(url_for('setorLista'))
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
        nome = current_user.nome
        email =  current_user.email
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
            flash('Sua mensagem foi enviada com sucesso! Fique atento no seu email', 'success')
        else:
            flash('Ocorreu um erro ao enviar a mensagem. Tente novamente.', 'error')

        return redirect(url_for('suporte'))

    return render_template('suporte.html')


@app.route('/setor/<int:setor_id>/add_professor', methods=['GET', 'POST'])
def add_professor(setor_id):
    form = ProfessorForm()
    setor = Setor.query.get_or_404(setor_id)
    if form.validate_on_submit():
        novo_professor = Professor(
            nome=form.nome.data,
            email=form.email.data,
            setor_id=setor_id
        )
        db.session.add(novo_professor)
        db.session.commit()
        return redirect(url_for('manage_professores', setor_id=setor_id))
    return render_template('professor/add_professor.html', form=form, setor=setor)

@app.route('/setor/<int:setor_id>/professores', methods=['GET'])
def manage_professores(setor_id):
    setor = Setor.query.get_or_404(setor_id)
    pesquisa = request.args.get('pesquisa', '')
    if pesquisa:
        professores = Professor.query.filter(Professor.nome.ilike(f"%{pesquisa}%"), Professor.setor_id == setor_id).order_by(Professor.nome).all()
    else:
        professores = setor.professores
    return render_template('professor/manage_professores.html', setor=setor, professores=professores)

@app.route('/setor/<int:setor_id>/professor/<int:id>/edit', methods=['GET', 'POST'])
def edit_professor(setor_id, id):
    professor = Professor.query.get_or_404(id)
    if request.method == 'POST':
        professor.nome = request.form['nome']
        professor.email = request.form['email']
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

@app.route('/editarPerfil/<int:id>/edit', methods=['GET', 'POST'])
def edit_perfil(id):
    perfil = User.query.get_or_404(id)
    if request.method == 'POST':
        nome_antigo = perfil.nome
        nome_novo = request.form['nome']
        perfil.nome = nome_novo

        professor = Professor.query.filter_by(nome=nome_antigo).first()
        if professor:
            professor.nome = nome_novo
        
        db.session.commit()
        return redirect(url_for('homepage'))
    
    return render_template('edit_perfil.html', perfil=perfil)

@app.route('/download-excel')
def download_excel():
    # Consultar dados dos setores
    setores = Setor.query.all()
    setores_list = [{'Nome': setor.nome} for setor in setores]

    # Consultar dados dos professores
    professores = Professor.query.all()
    professores_list = [{'Nome': professor.nome, 'Email': professor.email, 'Setor': professor.setor.nome} for professor in professores]

    # Consultar dados das aulas
    aulas = Aula.query.all()
    aulas_list = [{'Matéria': aula.materia, 'Sala': aula.sala, 'Dia': aula.dia, 'Horário Início': aula.horario_inicio, 'Horário Fim': aula.horario_fim, 'Professor': aula.professor.nome} for aula in aulas]

    # Consultar dados do suporte
    suportes = Suporte.query.all()
    suportes_list = [{'Nome': suporte.nome, 'Email': suporte.email, 'Mensagem': suporte.mensagem} for suporte in suportes]
    
    # Converter os dados em DataFrames do pandas
    df_setores = pd.DataFrame(setores_list)
    df_professores = pd.DataFrame(professores_list)
    df_aulas = pd.DataFrame(aulas_list)
    df_suportes = pd.DataFrame(suportes_list)

    # Salvar os DataFrames em um arquivo Excel na memória, cada um em uma aba
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_setores.to_excel(writer, index=False, sheet_name='Setores')
        df_professores.to_excel(writer, index=False, sheet_name='Professores')
        df_aulas.to_excel(writer, index=False, sheet_name='Aulas')
        df_suportes.to_excel(writer, index=False, sheet_name='Suportes')
    output.seek(0)

    # Enviar o arquivo para o cliente
    return send_file(output, download_name="dados.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/download-excel-professor')
def download_excel_professor():
    # Consultar o professor com o mesmo email do usuário logado
    professor = Professor.query.filter_by(email=current_user.email).first()
    if not professor:
        return "Usuário logado não é um professor", 403

    # Consultar dados das aulas do professor logado
    aulas = Aula.query.filter_by(professor_id=professor.id).all()
    
    # Debug: verificar os dados retornados
    print("Aulas do professor logado:", aulas)

    aulas_list = [{'Matéria': aula.materia, 'Sala': aula.sala, 'Dia': aula.dia, 'Horário Início': aula.horario_inicio, 'Horário Fim': aula.horario_fim} for aula in aulas]
    
    # Debug: verificar a lista de aulas
    print("Lista de aulas formatada:", aulas_list)

    # Converter os dados em um DataFrame do pandas
    df_aulas = pd.DataFrame(aulas_list)
    
    # Debug: verificar o DataFrame
    print("DataFrame das aulas:", df_aulas)

    # Salvar o DataFrame em um arquivo Excel na memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_aulas.to_excel(writer, index=False, sheet_name='Aulas')
    output.seek(0)

    # Enviar o arquivo para o cliente
    return send_file(output, download_name="aulas_professor.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/chats')
def chats():
    chats = current_user.chats
    return render_template('chat/chats.html', chats=chats)

@app.route('/chats/create', methods=['GET', 'POST'])
def create_chat():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user and user != current_user:
                # Verificar se o chat já existe
                existing_chat = Chat.query.filter(Chat.users.any(id=current_user.id)).filter(Chat.users.any(id=user.id)).first()
                if existing_chat:
                    flash('Chat já existe.')
                    return redirect(url_for('chats'))
                # Criar um novo chat
                new_chat = Chat(users=[current_user, user])
                db.session.add(new_chat)
                db.session.commit()
                return redirect(url_for('view_chat', chat_id=new_chat.id))
            else:
                flash('Usuário inválido.')
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('chat/create_chat.html', users=users)

@app.route('/chats/<int:chat_id>')
def view_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.users:
        flash('Você não tem permissão para acessar este chat.')
        return redirect(url_for('chats'))
    return render_template('chat/view_chat.html', chat=chat)

@app.route('/chats/<int:chat_id>/send', methods=['POST'])
def send_message(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.users:
        flash('Você não tem permissão para acessar este chat.')
        return redirect(url_for('chats'))
    content = request.form.get('content')
    if content:
        new_message = Message(content=content, sender=current_user, chat=chat)
        db.session.add(new_message)
        db.session.commit()
    return redirect(url_for('view_chat', chat_id=chat.id))
