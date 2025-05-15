import os
from flask import Flask, request, make_response, redirect, render_template, session, flash, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .forms import LoginForm, RegisterForm
from .models import User
from . import db
from datetime import datetime

def register_routes(app):
    from app.models import User, db
    # PAGINA PRINCIPAL
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return redirect(url_for('login'))
    
    @app.route('/inicio')
    def inicio():
        if 'username' not in session:
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        return render_template('Inicio.html', user=user)

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
            identidad = request.form.get('identidad')
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
                # El modelo espera 'preference' como 'male', 'female', 'both'
                if intereses == 'Mujeres':
                    user.preference = 'female'
                elif intereses == 'Hombres':
                    user.preference = 'male'
                elif intereses == 'Ambos':
                    user.preference = 'both'

            # Actualiza identidad (gender)
            if identidad:
                # El modelo espera 'gender' como 'male', 'female', 'other'
                if identidad == 'Heterosexual':
                    user.gender = 'male'
                elif identidad == 'Homosexual':
                    user.gender = 'female'
                elif identidad == 'Bisexual':
                    user.gender = 'other'
                elif identidad == 'Otro':
                    user.gender = 'other'

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

            # Guardar imagen de perfil
            file = request.files.get('profile_pic')
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                upload_path = os.path.join(upload_folder, filename)
                file.save(upload_path)
                user.profile_pic = f'uploads/{filename}'

            db.session.commit()
            flash("Perfil actualizado correctamente.")
            session['username'] = user.username

        return render_template('Perfil.html', user=user)