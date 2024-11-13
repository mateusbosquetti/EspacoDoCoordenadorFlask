from app import app, db, bcrypt
from flask import jsonify, render_template, url_for, request, redirect, flash, send_file
from app.forms import SetorForm, UserForm, LoginForm, ProfessorForm
from app.models import Setor, User, Suporte, Professor, Aula, DEFAULT_PROFILE_PICTURE_URL
from flask_login import login_user, logout_user, current_user
from datetime import time
from io import BytesIO
import pandas as pd
import requests
import cloudinary.uploader

@app.route('/home', methods=['GET','POST'])
def homepage():
    return render_template('index.html')

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error_message = None 

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None:
            error_message = 'Usuário não encontrado.'
        elif not bcrypt.check_password_hash(user.senha, form.senha.data):
            error_message = 'Senha incorreta.'
        else:
            login_user(user, remember=True)
            return redirect(url_for('homepage'))

    return render_template('login.html', form=form, error_message=error_message)

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = UserForm()
    error_message = None 

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            error_message = "O email já está em uso. Por favor, escolha outro email."
        elif form.senha.data != form.confirmacao_senha.data:
            error_message = "As senhas não correspondem. Por favor, tente novamente."   
        else:
            user = form.save()
            return redirect(url_for('homepage'))

    return render_template('cadastro.html', form=form, error_message=error_message)


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
    error_message = None 

    if request.method == 'POST':
        nome = current_user.nome
        email = current_user.email
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
            error_message = "Enviado com Sucesso!"
        else:
            error_message = "Erro! Mensagem não enviada"

        return render_template('suporte.html', error_message=error_message) 

    return render_template('suporte.html', error_message=error_message)


@app.route('/setor/<int:setor_id>/add_professor', methods=['GET', 'POST'])
def add_professor(setor_id):
    setor = Setor.query.get_or_404(setor_id)
    
    usuarios_elegiveis = User.query.filter(
        User.adm == False,
        ~User.id.in_([professor.id for professor in setor.professores])
    ).all()
    
    form = ProfessorForm()
    form.usuario.choices = [(user.id, f"{user.nome}") for user in usuarios_elegiveis]

    if form.validate_on_submit():
        usuario_selecionado = User.query.get(form.usuario.data)
        if usuario_selecionado:
            novo_professor = Professor(
                nome=usuario_selecionado.nome,
                email=usuario_selecionado.email,
                setor_id=setor_id
            )
            db.session.add(novo_professor)
            db.session.commit()
            return redirect(url_for('manage_professores', setor_id=setor_id))
        else:
            flash("Usuário selecionado não encontrado.", "danger")
    
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
    
    user = User.query.filter_by(email=professor.email, nome=professor.nome).first()
    profile_picture = user.profile_picture if user else DEFAULT_PROFILE_PICTURE_URL

    return render_template('professor/edit_professor.html', professor=professor, profile_picture=profile_picture)

@app.route('/setor/<int:setor_id>/professor/<int:id>/delete', methods=['GET'])
def delete_professor(setor_id, id):
    professor = Professor.query.get_or_404(id)
    db.session.delete(professor)
    db.session.commit()
    return redirect(url_for('manage_professores', setor_id=setor_id))

@app.route('/setor/<int:id>/delete', methods=['GET'])
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

@app.route('/adicionar_aula/<int:professor_id>', methods=['GET', 'POST'])
def adicionar_aula(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    if request.method == 'POST':
        materia = request.form['materia']
        sala = request.form['sala'] 
        dia = request.form['dia']
        horario_inicio = time.fromisoformat(request.form['horario_inicio'])
        horario_fim = time.fromisoformat(request.form['horario_fim'])
        
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
    
    return render_template('aula/adicionar_aula.html', professor=professor)



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

@app.route('/professor/<int:professor_id>/aula/<int:id>/delete', methods=['GET'])
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

        if 'profile_picture' in request.files:
            file_to_upload = request.files['profile_picture']
            if file_to_upload:

                upload_result = cloudinary.uploader.upload(
                    file_to_upload,
                    transformation=[
                        {'width': 200, 'height': 200, 'crop': 'fill'}
                    ]
                )
                perfil.profile_picture = upload_result['secure_url']

        db.session.commit()

    return render_template('edit_perfil.html', perfil=perfil)


@app.route('/download-excel')
def download_excel():
    setores = Setor.query.all()
    setores_list = [{'Nome': setor.nome} for setor in setores]

    professores = Professor.query.all()
    professores_list = [{'Nome': professor.nome, 'Email': professor.email, 'Setor': professor.setor.nome} for professor in professores]

    aulas = Aula.query.all()
    aulas_list = [{'Matéria': aula.materia, 'Sala': aula.sala, 'Dia': aula.dia, 'Horário Início': aula.horario_inicio, 'Horário Fim': aula.horario_fim, 'Professor': aula.professor.nome} for aula in aulas]

    suportes = Suporte.query.all()
    suportes_list = [{'Nome': suporte.nome, 'Email': suporte.email, 'Mensagem': suporte.mensagem} for suporte in suportes]
    
    df_setores = pd.DataFrame(setores_list)
    df_professores = pd.DataFrame(professores_list)
    df_aulas = pd.DataFrame(aulas_list)
    df_suportes = pd.DataFrame(suportes_list)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_setores.to_excel(writer, index=False, sheet_name='Setores')
        df_professores.to_excel(writer, index=False, sheet_name='Professores')
        df_aulas.to_excel(writer, index=False, sheet_name='Aulas')
        df_suportes.to_excel(writer, index=False, sheet_name='Suportes')
    output.seek(0)

    return send_file(output, download_name="dados.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/download-excel-professor')
def download_excel_professor():

    professor = Professor.query.filter_by(email=current_user.email).first()
    if not professor:
        return "Usuário logado não é um professor", 403

    aulas = Aula.query.filter_by(professor_id=professor.id).all()
    
    print("Aulas do professor logado:", aulas)

    aulas_list = [{'Matéria': aula.materia, 'Sala': aula.sala, 'Dia': aula.dia, 'Horário Início': aula.horario_inicio, 'Horário Fim': aula.horario_fim} for aula in aulas]
    
    print("Lista de aulas formatada:", aulas_list)

    df_aulas = pd.DataFrame(aulas_list)
    
    print("DataFrame das aulas:", df_aulas)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_aulas.to_excel(writer, index=False, sheet_name='Aulas')
    output.seek(0)

    return send_file(output, download_name="aulas_professor.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/dashboard')
def dashboard():
    total_setores = Setor.query.count()
    total_professores = Professor.query.count()
    total_aulas = Aula.query.count()
    total_suportes = Suporte.query.count()
    
    recentes_suportes = Suporte.query.order_by(Suporte.id.desc()).limit(5).all()

    return render_template('dashboard.html', 
                           total_setores=total_setores, 
                           total_professores=total_professores,
                           total_aulas=total_aulas, 
                           total_suportes=total_suportes,
                           recentes_suportes=recentes_suportes)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    error_message = None 

    if request.method == 'POST':
        institution_name = request.form['institution_name']
        contact_name = request.form['contact_name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        staticforms_url = "https://api.staticforms.xyz/submit"
        data = {
            "accessKey": "c9e5c3a3-07ee-4249-8818-e89aab33b38f", 
            "institution_name": institution_name,
            "name": contact_name,
            "email": email,
            "phone": phone,
            "message": message,
            "redirectTo": url_for('contact', _external=True)
        }
        response = requests.post(staticforms_url, data=data)

        if response.status_code == 200:
            error_message = "Mensagem enviada com sucesso!"
        else:
            error_message = "Erro! Mensagem não enviada."

        return render_template('contact.html', error_message=error_message)

    return render_template('contact.html', error_message=error_message)

@app.route('/usuarios')
def listar_usuarios():

    usuarios = User.query.order_by(User.adm.desc()).all()
    return render_template('usuario/listar_usuarios.html', usuarios=usuarios)

@app.route('/usuarios/excluir/<int:id>')
def excluir_usuario(id):
    usuario = User.query.get(id)
    if usuario.adm:
        flash('Não é possível excluir um administrador.')
        return redirect(url_for('listar_usuarios'))
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso!')
    return redirect(url_for('listar_usuarios'))

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = User.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']

        if request.form['senha']:
            usuario.senha = request.form['senha']
        db.session.commit()
        flash('Usuário atualizado com sucesso!')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuario/editar_usuario.html', usuario=usuario)

from flask import render_template, request
from flask_socketio import emit
from app import db, socketio
from app.models import Message
from flask_login import current_user

@app.route('/chat')
def chat():
    messages = db.session.query(Message, User).join(User, Message.user_id == User.id).order_by(Message.timestamp).all()
    users = User.query.all() 
    current_user_name = current_user.nome
    return render_template('chat.html', messages=messages, users=users, current_user_name=current_user_name)

@socketio.on('send_message')
def handle_send_message(data):
    content = data.get('content')
    user_id = current_user.id  
    user_name = current_user.nome  

    message = Message(content=content, user_id=user_id)
    db.session.add(message)
    db.session.commit()

    emit('receive_message', {
        'user_name': user_name,
        'content': content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

@app.route('/sobre', methods=['GET'])
def sobre():
    return render_template('sobre_nos.html')