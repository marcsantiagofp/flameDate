from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, IntegerField, RadioField, MultipleFileField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional

# Formulario de login
class LoginForm(FlaskForm):
    username = StringField('Nom d\'usuari', validators=[DataRequired()])
    password = PasswordField('Contrasenya', validators=[DataRequired()])
    submit = SubmitField('Iniciar sessió')

# Formulario de registro SOLO con los campos obligatorios del HTML
class RegisterForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=100)])
    email = EmailField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Repetir contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir.')])
    submit = SubmitField('Registrarse')

# Formulario para actualizar el perfil de usuario (FlameDate)
class UpdatePerfilForm(FlaskForm):
    username = StringField('Nombre', validators=[DataRequired()])
    edad = IntegerField('Edad', validators=[Optional()])
    intereses = SelectField('Intereses', choices=[('Mujeres', 'Mujeres'), ('Hombres', 'Hombres'), ('Ambos', 'Ambos')], validators=[Optional()])
    identidad = SelectField('Identidad', choices=[('Heterosexual', 'Heterosexual'), ('Homosexual', 'Homosexual'), ('Bisexual', 'Bisexual'), ('Otro', 'Otro')], validators=[Optional()])
    sex_ori = StringField('Orientación sexual', validators=[Optional()])  # Añadido
    busca = RadioField('Busco', choices=[
        ('red', '😍 RELACIÓN ESTABLE'),
        ('yellow', '😅 ROLLOS CORTOS'),
        ('blue', '🤝 HACER AMIGOS'),
        ('sparkle', '✨ LO QUE SURJA')
    ], validators=[Optional()])
    images = MultipleFileField('Subir imágenes')
    delete_images = HiddenField('Imágenes a eliminar (ids separadas por coma)')
    submit = SubmitField('Actualizar')

class UpdateUserForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    marca = StringField('Marca')
    modelo = StringField('Modelo')
    matricula = StringField('Matrícula')
    tipo_vehiculo = SelectField('Tipo de Vehículo', choices=[('coche', 'Coche'), ('moto', 'Moto'), ('bicicleta', 'Bicicleta')])

class PasswordChangeForm(FlaskForm):
    nueva_contrasena = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=6)])
    confirmar_contrasena = PasswordField('Confirmar Contraseña', validators=[DataRequired()])

