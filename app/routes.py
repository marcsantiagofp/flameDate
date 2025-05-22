import os
from flask import Flask, request, make_response, redirect, render_template, session, flash, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .forms import LoginForm, RegisterForm
from .models import User, Matches, Flames, Message, UserImage
from . import db
from datetime import datetime

# Variable global para guardar la última acción del ESP32
esp32_action = {'action': 'none'}

def register_routes(app):
    from app.models import User, db
    # PAGINA PRINCIPAL
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return redirect(url_for('login'))
    
    @app.route('/inicio', methods=['GET', 'POST'])
    def inicio():
        if 'username' not in session:
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        # Get flames (mutual matches)
        flames = Flames.query.filter(
            (Flames.user1_id == user.id) | (Flames.user2_id == user.id)
        ).all()
        flame_users = set()
        for flame in flames:
            if flame.user1_id == user.id:
                flame_users.add(flame.user2_id)
            else:
                flame_users.add(flame.user1_id)
        # Obtener rango de edad de la request (GET o POST)
        min_age = request.values.get('minAge', default=18, type=int)
        max_age = request.values.get('maxAge', default=30, type=int)
        # Filtrar usuarios según preferencia y rango de edad
        query = User.query.filter(
            (User.username != session['username']) & (~User.id.in_(flame_users))
        )
        if user.preference == 'male':
            query = query.filter(User.gender == 'male')
        elif user.preference == 'female':
            query = query.filter(User.gender == 'female')
        elif user.preference == 'both':
            query = query.filter(User.gender.in_(['male', 'female']))
        # Filtrar por rango de edad si existe el campo age
        query = query.filter(User.age >= min_age, User.age <= max_age)
        users = query.all()
        # For display in flames list
        flame_users_display = [User.query.get(uid) for uid in flame_users]
        images = user.images.order_by(UserImage.uploaded_at.asc()).all()
        profile_pic = images[0].filename if images else 'images/perfil.jpg'
        return render_template(
            'Inicio.html',
            user=user,
            users=users,
            flame_users=flame_users_display,
            profile_pic=profile_pic,
            min_age=min_age,
            max_age=max_age
        )

    # USUARIOS 
    # Ruta para la página de registro
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            gender = request.form.get('gender')  # Nuevo campo para género

            # Validación básica
            if not username or not email or not password or not confirm_password:
                flash("Todos los campos son obligatorios.")
                return render_template('Registro.html', register_form=form)

            if password != confirm_password:
                flash("Las contraseñas no coinciden.")
                return render_template('Registro.html', register_form=form)

            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash("Ya existe un usuario con ese nombre o email.")
                return render_template('Registro.html', register_form=form)

            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            if gender:
                new_user.gender = gender
            db.session.add(new_user)
            db.session.commit()
            flash("Usuario creado correctamente. ¡Ahora puedes iniciar sesión!")
            return redirect(url_for('login'))

        return render_template('Registro.html', register_form=form)

    # Ruta para la página de login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                flash('Todos los campos son obligatorios.')
                return render_template('Inicio_Sesion.html', form=form)

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['username'] = username
                flash('Inicio de sesión exitoso!')
                return redirect(url_for('inicio'))
            else:
                flash('Nombre de usuario o contraseña incorrectos.')

        return render_template('Inicio_Sesion.html', form=form)

    # Cerrar session
    @app.route('/logout')
    def logout():
        session.pop('username', None)
        flash("Has cerrado sesión correctamente.")
        return redirect(url_for('index'))  # Redirige a la página de inicio

    # Ruta para borrar usuario
    @app.route('/borrar_usuario', methods=['POST'])
    def borrar_usuario():
        if 'username' not in session:
            flash("Debes iniciar sesión para realizar esta acción.")
            return redirect(url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash("Usuario no encontrado.")
            return redirect(url_for('info_usuario'))

        db.session.delete(user)
        db.session.commit()
        session.pop('username', None)
        flash("Tu cuenta ha sido eliminada correctamente.")
        return redirect(url_for('index'))

    # Ruta para ver y actualizar el perfil del usuario (FlameDate)
    @app.route('/perfil', methods=['GET', 'POST'])
    def perfil():
        if 'username' not in session:
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash("Usuario no encontrado.")
            return redirect(url_for('login'))

        if request.method == 'POST':
            username = request.form.get('username')
            edad = request.form.get('edad')
            intereses = request.form.get('intereses')
            gender = request.form.get('gender')  # <-- Recoge el valor del select de género
            sex_ori = request.form.get('sex_ori')
            busca = request.form.get('busca')

            # Actualiza nombre de usuario
            if username:
                user.username = username

            # Actualiza edad
            if edad:
                try:
                    user.age = int(edad)
                except ValueError:
                    pass

            # Actualiza preferencias (intereses)
            if intereses:
                if intereses == 'Mujeres':
                    user.preference = 'female'
                elif intereses == 'Hombres':
                    user.preference = 'male'
                elif intereses == 'Ambos':
                    user.preference = 'both'

            # Actualiza género (gender)
            if gender in ['male', 'female', 'other']:
                user.gender = gender

            # Actualiza orientación sexual
            if sex_ori:
                user.sex_ori = sex_ori

            # Actualiza bio con lo que busca
            if busca:
                # Puedes guardar el valor de busca en bio o crear un campo específico
                # Aquí lo guardamos en bio como ejemplo
                if busca == 'red':
                    user.bio = '😍 RELACIÓN ESTABLE'
                elif busca == 'yellow':
                    user.bio = '😅 ROLLOS CORTOS'
                elif busca == 'blue':
                    user.bio = '🤝 HACER AMIGOS'
                elif busca == 'sparkle':
                    user.bio = '✨ LO QUE SURJA'

            # Eliminar imágenes seleccionadas
            delete_images = request.form.get('delete_images', '')
            if delete_images:
                ids = [int(i) for i in delete_images.split(',') if i.strip().isdigit()]
                for img_id in ids:
                    img = UserImage.query.filter_by(id=img_id, user_id=user.id).first()
                    if img:
                        # Borra el archivo físico si existe
                        img_path = os.path.join(app.root_path, 'static', img.filename)
                        if os.path.exists(img_path):
                            os.remove(img_path)
                        db.session.delete(img)

            # Subir nuevas imágenes
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    upload_path = os.path.join(upload_folder, filename)
                    file.save(upload_path)
                    rel_path = f'uploads/{filename}'
                    db.session.add(UserImage(user_id=user.id, filename=rel_path))

            db.session.commit()
            flash("Perfil actualizado correctamente.")
            session['username'] = user.username

        images = user.images.order_by(UserImage.uploaded_at.asc()).all()
        profile_pic = images[0].filename if images else 'images/perfil.jpg'
        return render_template('Perfil.html', user=user, images=images, profile_pic=profile_pic)

    # Ruta para mostrar la configuración del usuario (configuración de búsqueda)
    @app.route('/config', methods=['GET', 'POST'])
    def config():
        if 'username' not in session:
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash("Usuario no encontrado.")
            return redirect(url_for('login'))

        # Aquí puedes manejar POST si quieres guardar preferencias de búsqueda
        if request.method == 'POST':
            # Ejemplo: guardar distancia y rango de edad si los añades al modelo
            distancia = request.form.get('distanceRange')
            min_edad = request.form.get('minAge')
            max_edad = request.form.get('maxAge')
            # user.distancia = distancia
            # user.min_edad = min_edad
            # user.max_edad = max_edad
            # db.session.commit()
            flash("Configuración actualizada correctamente.")

        return render_template('Inicio.html', user=user, show_config=True)

    @app.route('/like', methods=['POST'])
    def like():
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        user = User.query.filter_by(username=session['username']).first()
        liked_user_id = request.json.get('liked_user_id')
        if not liked_user_id:
            return jsonify({'success': False, 'message': 'ID de usuario no proporcionado'}), 400
        # Evitar duplicados
        existing = Matches.query.filter_by(user_id=user.id, liked_user_id=liked_user_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Ya le diste like'}), 200
        match = Matches(user_id=user.id, liked_user_id=liked_user_id)
        db.session.add(match)
        db.session.commit()
        # Check for mutual like
        mutual = Matches.query.filter_by(user_id=liked_user_id, liked_user_id=user.id).first()
        if mutual:
            # Avoid duplicate flames
            already_flame = Flames.query.filter(
                ((Flames.user1_id == user.id) & (Flames.user2_id == liked_user_id)) |
                ((Flames.user1_id == liked_user_id) & (Flames.user2_id == user.id))
            ).first()
            if not already_flame:
                flame = Flames(user1_id=user.id, user2_id=liked_user_id)
                db.session.add(flame)
                db.session.commit()
            return jsonify({'success': True, 'message': '¡Es un flame!', 'flame': True})
        return jsonify({'success': True, 'message': 'Like registrado', 'flame': False})

    @app.route('/chats', methods=['GET', 'POST'])
    def chats():
        if 'username' not in session:
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        # Get flames (mutual matches)
        flames = Flames.query.filter(
            (Flames.user1_id == user.id) | (Flames.user2_id == user.id)
        ).all()
        flame_users = set()
        for flame in flames:
            if flame.user1_id == user.id:
                flame_users.add(flame.user2_id)
            else:
                flame_users.add(flame.user1_id)
        flame_users_display = [User.query.get(uid) for uid in flame_users]
        chat_user_id = request.args.get('user_id', type=int)
        chat_user = None
        messages = []
        # Mostrar el chat con el ultimo usuario con el que se chateó
        if not chat_user_id and flame_users:
            last_msg = (
                Message.query.filter(
                    ((Message.sender_id == user.id) & (Message.receiver_id.in_(flame_users))) |
                    ((Message.sender_id.in_(flame_users)) & (Message.receiver_id == user.id))
                )
                .order_by(Message.timestamp.desc())
                .first()
            )
            if last_msg:
                if last_msg.sender_id == user.id:
                    chat_user_id = last_msg.receiver_id
                else:
                    chat_user_id = last_msg.sender_id
        if chat_user_id:
            chat_user = User.query.get(chat_user_id)
            if chat_user and chat_user.id in flame_users:
                if request.method == 'POST':
                    content = request.form.get('message')
                    if content:
                        new_msg = Message(sender_id=user.id, receiver_id=chat_user.id, content=content)
                        db.session.add(new_msg)
                        db.session.commit()
                messages = Message.query.filter(
                    ((Message.sender_id == user.id) & (Message.receiver_id == chat_user.id)) |
                    ((Message.sender_id == chat_user.id) & (Message.receiver_id == user.id))
                ).order_by(Message.timestamp.asc()).all()
        return render_template('Chats.html', user=user, flame_users=flame_users_display, chat_user=chat_user, messages=messages)

    @app.route('/user_photos/<int:user_id>')
    def user_photos(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({'images': []})
        images = [
            url_for('static', filename=img.filename)
            for img in user.images.order_by(UserImage.uploaded_at.asc()).all()
        ]
        return jsonify({'images': images})
    
    # Endpoint que recibe la señal del ESP32
    @app.route('/esp32', methods=['POST'])
    def esp32_trigger():
        global esp32_action
        data = request.get_json()
        valor = data.get('valor')
        if valor is True:
            esp32_action['action'] = 'like'
        elif valor is False:
            esp32_action['action'] = 'nope'
        else:
            esp32_action['action'] = 'none'
        return jsonify({'ok': True})

    # Endpoint que consulta el frontend para saber si hay acción pendiente
    @app.route('/esp32_poll')
    def esp32_poll():
        global esp32_action
        action = esp32_action['action']
        esp32_action['action'] = 'none'  # Resetea después de leer
        return jsonify({'action': action})