from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

class AuthService:

    @staticmethod
    def register_user(data):
        # Cek duplikat
        if User.query.filter_by(username=data['username']).first():
            raise ValueError("Username already exists")
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already exists")

        hashed_password = generate_password_hash(data['password'])
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login_user(data):
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            raise ValueError("Invalid credentials")
        if not check_password_hash(user.password_hash, data['password']):
            raise ValueError("Invalid credentials")

        token = create_access_token(identity=str(user.id))
        return token, user