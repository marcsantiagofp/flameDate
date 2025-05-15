from . import db
from datetime import datetime

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=True)
    preference = db.Column(db.Enum('male', 'female', 'both'), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'