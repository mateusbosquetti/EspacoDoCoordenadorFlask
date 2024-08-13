from app import app, db
from flask import jsonify, render_template, url_for, request, redirect, flash, send_file
from app.forms import SetorForm, UserForm, LoginForm, ProfessorForm
from app.models import Setor, User, Suporte, Professor, Aula, Chat, Message
from flask_login import login_user, logout_user, current_user
from datetime import time
from io import BytesIO
import pandas as pd
import requests
import cloudinary.uploader

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
        return redirect(url_for('homepage'))
    return render_template('cadastro.html', form=form)

@app.route('/sair/')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/setor/', methods=['GET', 'POST'])
def setor():
    form = SetorForm()
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('setorLista'))
    return render_template('setor/setores.html', form=form)

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
    professor_data = []

    if pesquisa:
        professores = Professor.query.filter(Professor.nome.ilike(f"%{pesquisa}%"), Professor.setor_id == setor_id).order_by(Professor.nome).all()
    else:
        professores = setor.professores

    for professor in professores:
        user = User.query.filter_by(email=professor.email, nome=professor.nome).first()
        if user:
            profile_picture = user.profile_picture
        else:
            profile_picture = DEFAULT_PROFILE_PICTURE_URL
        professor_data.append({
            'id': professor.id,
            'nome': professor.nome,
            'email': professor.email,
            'profile_picture': profile_picture
        })

    return render_template('professor/manage_professores.html', setor=setor, professores=professor_data)

@app.route('/setor/<int:setor_id>/professor/<int:id>/edit', methods=['GET', 'POST'])
def edit_professor(setor_id, id):
    professor = Professor.query.get_or_404(id)
    if request.method == 'POST':
        professor.nome = request.form['nome']
        professor.email = request.form['email']
        db.session.commit()
        return redirect(url_for('manage_professores', setor_id=setor_id))
    
    # Buscar o usuário para obter a foto
    user = User.query.filter_by(email=professor.email, nome=professor.nome).first()
    profile_picture = user.profile_picture if user else DEFAULT_PROFILE_PICTURE_URL

    return render_template('professor/edit_professor.html', professor=professor, profile_picture=profile_picture)

@app.route('/setor/<int:setor_id>/professor/<int:id>/delete', methods=['POST'])
def delete_professor(setor_id, id):
    professor = Professor.query.get_or_404(id)
    db.session.delete(professor)
    db.session.commit()
    return redirect(url_for('manage_professores', setor_id=setor_id))

@app.route('/setor/<int:id>/delete', methods=['POST'])
def delete_setor(id):
    setor = Setor.query.get_or_404(id)
    db.session.delete(setor)
    db.session.commit()
    return redirect(url_for('setorLista'))


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

        # Upload da nova foto de perfil, se fornecida
        if 'profile_picture' in request.files:
            file_to_upload = request.files['profile_picture']
            if file_to_upload:
                # Redimensionar a imagem para 200x200 pixels
                upload_result = cloudinary.uploader.upload(
                    file_to_upload,
                    transformation=[
                        {'width': 200, 'height': 200, 'crop': 'fill'}
                    ]
                )
                perfil.profile_picture = upload_result['secure_url']

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
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


from .models import DEFAULT_PROFILE_PICTURE_URL, Chat, Message, User, db

@app.route('/chats')
def chats():
    chats = current_user.chats
    chats_with_last_message = []
    for chat in chats:
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).first()
        if last_message:
            # Limita a última mensagem a 35 caracteres e adiciona "..." se necessário
            truncated_message = (last_message.content[:35] + '...') if len(last_message.content) > 35 else last_message.content
            last_message.content = truncated_message
        chats_with_last_message.append((chat, last_message))

    users = User.query.filter(User.id != current_user.id).all()
    return render_template('chat/chats.html', chats=chats_with_last_message, users=users)


@app.route('/chats/<int:chat_id>/json')
def chat_json(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.users:
        return jsonify({'error': 'Você não tem permissão para acessar este chat.'}), 403
    messages = [{
        'sender_nome': msg.sender.nome,
        'sender_sobrenome': msg.sender.sobrenome,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    } for msg in chat.messages]
    return jsonify({
        'chat_name': chat.name if chat.is_group else 'Chat',
        'messages': messages
    })

@app.route('/chats/create', methods=['POST'])
def create_chat():
    user_ids = request.form.getlist('user_ids')
    chat_name = request.form.get('chat_name')

    if user_ids:
        users = User.query.filter(User.id.in_(user_ids)).all()
        if not users or (len(users) == 1 and users[0] == current_user):
            return jsonify({'error': 'Não é possível criar um chat consigo mesmo ou sem usuários válidos.'}), 400

        is_group = len(users) > 1

        if is_group:
            if not chat_name:
                return jsonify({'error': 'Nome do grupo é obrigatório.'}), 400
            if Chat.query.filter_by(name=chat_name).first():
                return jsonify({'error': 'Já existe um grupo com esse nome.'}), 400
            
            user_ids_set = set(user_ids)
            existing_groups = Chat.query.filter(Chat.is_group == True).all()
            for group in existing_groups:
                group_user_ids_set = {str(user.id) for user in group.users}
                if user_ids_set == group_user_ids_set:
                    return jsonify({'error': 'Já existe um grupo com esses usuários.'}), 400


        if not is_group:
            existing_chat = Chat.query.filter(
                Chat.is_group == False,
                Chat.users.any(id=current_user.id),
                Chat.users.any(id=users[0].id)
            ).first()
            if existing_chat:
                return jsonify({'error': 'Chat individual já existe.'}), 400

        new_chat = Chat(users=[current_user] + users, is_group=is_group, name=chat_name if is_group else None)
        db.session.add(new_chat)
        db.session.commit()
        return jsonify({'success': True, 'chat_id': new_chat.id})

    return jsonify({'error': 'Usuários não selecionados.'}), 400

@app.route('/chats/<int:chat_id>/send', methods=['POST'])
def send_message(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.users:
        return jsonify({'error': 'Você não tem permissão para acessar este chat.'}), 403

    content = request.form.get('content')
    if content:
        new_message = Message(content=content, sender=current_user, chat=chat)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'error': 'Conteúdo da mensagem vazio.'}), 400
