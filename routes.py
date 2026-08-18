from flask import Blueprint, jsonify, request
from models import User, Category, Product, Order
from utils import db
from werkzeug.security import generate_password_hash

users_bp        = Blueprint('users', __name__, url_prefix='')
products_bp     = Blueprint('products', __name__, url_prefix='/products')

# Hardcoded product data
hardcoded_products = [
    {"id": 1, "name": "Laptop Gaming", "Price": 15000000},
    {"id": 2, "name": "Mouse Wireless", "Price": 250000},
    {"id": 3, "name": "Keyboard Mechanical", "Price": 850000},
    ]


@products_bp.route('', methods=['GET'])
def get_products():
    # products = Product.query.all()
    return jsonify(hardcoded_products), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # product = Product.query.get(product_id)
    product = next((p for p in hardcoded_products if p['id'] == product_id), None)
    if product is None:
        return jsonify({"message": "Product not found", "status": "error"}), 404
    return jsonify(product), 200


@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    try:
        # Validasi input
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({"message": "Username, email, and password are required", "status": "error"}), 400
    
         # Cek email/username sudah terdaftar?
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"message": "Email already registered", "status": "error"}), 400
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"message": "Username already taken", "status": "error"}), 400
    
        # Hash password
        hashed_password = generate_password_hash(data['password'])
    
        # Buat user baru (role akan otomatis 'customer' dari default model)
        new_user = User(
            username        = data['username'],
            email           = data['email'],
            password_hash   = hashed_password
        )
    
        db.session.add(new_user)
        db.session.commit()
    
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "created_at": new_user.created_at
            }
        }), 201
        
    except Exception as e:
         db.session.rollback()
         return jsonify({"message": "Error creating users", "status": "error"}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User not found", "status": "error"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at
    }), 200
