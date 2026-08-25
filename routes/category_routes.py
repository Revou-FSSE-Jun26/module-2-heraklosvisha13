# CATEGORY ROUTES:
# 1. POST - /categories --> Create a new category
# 2. GET - /categories --> List all categories
# 3. GET - /categories/<id> --> Get a specific category along with its products
# 4. PUT - /categories/<id> --> Update a specific category
# 5. DELETE - /categories/<id> --> Delete a category (blocked if products exist)

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, Category
from flask_jwt_extended import jwt_required, get_jwt_identity

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

# -------------------------------------------------------------------
# 1. POST - /categories --> Create a new category
# -------------------------------------------------------------------
@categories_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    # Ambil user_id dari token (opsional, untuk logging)
    # current_user_id = get_jwt_identity()
    
    data = request.get_json()
    
    # 1. Check existing data
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # 2. Get data field
    category_name = data.get('category_name')

    # 3. validate input
    if not category_name:
        return jsonify({"error": "Category name is required"}), 400

    # 4. Validate data type and strip
    try:
        category_name = str(category_name).strip()
        if not category_name:
            return jsonify({"error": "Category name cannot be empty or only spaces"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Category must be a valid string"}), 400

    # 5. check existence category name (unique constraint)
    existing_category = Category.query.filter_by(category_name=category_name).first()
    if existing_category:
        return jsonify({"error": "Category with this name already exists"}), 409

    try:
        # Create new category
        new_category = Category(category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            "message": "Category created successfully",
            "data": new_category.to_dict()
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error: category may already exist"}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500

# -------------------------------------------------------------------
# 2. GET - /categories --> List all categories
# -------------------------------------------------------------------
@categories_bp.route('', methods=['GET'])
def list_all_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

# -------------------------------------------------------------------
# 3. GET - /categories/<id> --> Get a specific category along with its products
# -------------------------------------------------------------------
@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"message": "Category not found", "status": "error"}), 404
        # include_products=True akan menampilkan daftar produk dalam kategori ini
        return jsonify(category.to_dict(include_products=True)), 200
    
    except SQLAlchemyError as e:
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

# -------------------------------------------------------------------
# 4. PUT - /categories/<id> --> Update a specific category
# -------------------------------------------------------------------
@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    # 1. Cek apakah kategori ada
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "Category not found", "status": "error"}), 404

    # 2. Ambil data dari request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
        
    # Flag untuk mengecek apakah ada field yang diupdate
    updated = False

    # 3. Update field jika ada
    if 'category_name' in data:
        new_name = data['category_name']
        
        # Validasi: pastikan string tidak kosong
        if not new_name or not isinstance(new_name, str):
            return jsonify({"error": "Category name must be a non-empty string"}), 400
            
        new_name = new_name.strip()
        if not new_name:
            return jsonify({"error": "Category name cannot be empty or only spaces"}), 400
            
        if len(new_name) < 3:
            return jsonify({"error": "Category name must be at least 3 characters"}), 400
            
        # Cek apakah nama baru sudah digunakan oleh kategori lain (unique constraint)
        existing = Category.query.filter(Category.id != category_id, Category.category_name == new_name).first()
        if existing:
            return jsonify({"error": "Category name already exists for another category"}), 409
            
        # Set nama baru
        category.category_name = new_name
        updated = True

    # 4. Jika tidak ada field yang diupdate, kembalikan data tanpa perubahan
    if not updated:
        return jsonify({
            "message": "No fields to update",
            "data": category.to_dict(include_products=True)
        }), 200

    # 5. Simpan perubahan ke database dengan try-except
    try:
        db.session.commit()
        return jsonify({
            "message": "Category updated successfully",
            "data": category.to_dict(include_products=True)
        }), 200

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error: duplicate or invalid data"}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500

# -------------------------------------------------------------------   
# 5. DELETE - /categories/<id> --> Delete a category (blocked if products exist)
# -------------------------------------------------------------------
@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    # 1. Cek apakah kategori ada
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "Category not found", "status": "error"}), 404
    
    # 2. Cek apakah ada produk yang masih menggunakan kategori ini
    if category.products:
        return jsonify({
            "error": "Cannot delete category: products still exist in this category",
            "status": "error"
        }), 409
    
    # 3. Hapus kategori
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully", "status": "success"}), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500