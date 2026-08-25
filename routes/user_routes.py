# USER ROUTES:
# 1. POST - Registration
# 2. POST - Login

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import re

users_bp = Blueprint('users', __name__, url_prefix='/users')

# -------------------------------------------------------------------
# 1. POST - /users --> Register a new user
# -------------------------------------------------------------------
@users_bp.route('', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Validasi input
    if not username or not password or not email:
        return jsonify({"error": "Username, password, and email are required"}), 400

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters long"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({"error": "Invalid email format"}), 400

    
    # Cegah duplikat (manual + IntegrityError sebagai jaring pengaman)
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or email already exists"}), 400

    password_hash = generate_password_hash(password)

    try:    
        new_user = User(
            username=username,
            password_hash=password_hash,
            email=email
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "user": new_user.to_dict()}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception:
        db.session.rollback()
        # ✨ Konsisten dengan endpoint lain
        return jsonify({"error": "An unexpected error occurred"}), 500


# -------------------------------------------------------------------
# 2. POST - /auth/login --> User login
# -------------------------------------------------------------------
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=str(user.id))
    return jsonify({
        "message": "Login successfully",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200