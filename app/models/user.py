# models/user.py
from datetime import datetime
from . import db  # Import db dari __init__.py


class User(db.Model):
    __tablename__   = 'users'

    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(255), nullable=False, unique=True)
    password_hash   = db.Column(db.String(255), nullable=False)
    email           = db.Column(db.String(255), nullable=False, unique=True)
    role            = db.Column(db.String(20), server_default='customer')  # Added role field with default value
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    orders          = db.relationship('Order', backref='user', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at
        }