from flask import Flask, request, make_response, redirect, render_template, session, flash, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
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

    # INFORMACION USUARIO
    @app.route('/info_usuario', methods=['GET', 'POST'])
    def info_usuario():
        if 'username' not in session:
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash("Usuario no encontrado.")
            return redirect(url_for('login'))

        if request.method == 'POST':
            # Procesar los datos enviados según la sección
            if request.form.get('seccion') == 'usuario':
                nombre = request.form.get('nombre')
                apellidos = request.form.get('apellidos')
                email = request.form.get('email')
                telefono = request.form.get('telefono')
                
                if nombre:
                    user.username = nombre
                if apellidos:
                    user.apellido = apellidos
                if email:
                    user.email = email
                if telefono:
                    user.telefono = telefono

                db.session.commit()
                flash("Información del usuario actualizada correctamente.")

            elif request.form.get('seccion') == 'vehiculo':
                marca = request.form.get('marca')
                modelo = request.form.get('modelo')
                matricula = request.form.get('matricula')
                tipo = request.form.get('tipo')
                
                # Verificar si hay un vehículo asociado al usuario
                if marca or modelo or matricula or tipo:
                    if not user.vehiculo:
                        # Insertar un nuevo vehículo si no existe
                        vehiculo = Vehiculo(
                            marca=marca,
                            modelo=modelo,
                            matricula=matricula,
                            tipo=tipo,
                            user_id=user.id
                        )
                        db.session.add(vehiculo)
                        flash("Información del vehículo guardada correctamente.")
                    else:
                        # Si ya existe un vehículo, actualiza los datos
                        vehiculo = user.vehiculo
                        if marca:
                            vehiculo.marca = marca
                        if modelo:
                            vehiculo.modelo = modelo
                        if matricula:
                            vehiculo.matricula = matricula
                        if tipo:
                            vehiculo.tipo = tipo
                        flash("Información del vehículo actualizada correctamente.")

                db.session.commit()

            elif request.form.get('seccion') == 'contrasena':
                nueva_contrasena = request.form.get('nueva-contrasena')
                confirmar_contrasena = request.form.get('confirmar-contrasena')

                if nueva_contrasena and nueva_contrasena == confirmar_contrasena:
                    user.password = generate_password_hash(nueva_contrasena)
                    db.session.commit()
                    flash("Contraseña actualizada correctamente.")
                else:
                    flash("Las contraseñas no coinciden.")

        context = {
            "user": user
        }
        return render_template('Info_Usuario.html', **context)

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