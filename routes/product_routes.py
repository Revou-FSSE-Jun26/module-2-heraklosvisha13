# PRODUCT ROUTES:
# 1. POST - /products --> Create a new product
# 2. GET - /products --> List all products
# 3. GET - /products/<id> --> Get a specific product
# 4. PUT - /products/<id> --> Update a specific product
# 5. DELETE - /products/<id> --> Delete a product (if no order exists)

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, Product, Category, order_items
from flask_jwt_extended import jwt_required

products_bp = Blueprint('products', __name__, url_prefix='/products')

# -------------------------------------------------------------------
# 1. POST - /products --> Create a new product
# -------------------------------------------------------------------
@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock')
    category_id = data.get('category_id')

    if not name or not price or not stock or not category_id:
        return jsonify({"error": "Name, price, stock, and category id are required"}), 400

    # ✨ Validasi panjang name (konsisten dengan PUT dan user routes)
    if len(name) < 3:
        return jsonify({"error": "Name must be at least 3 characters long"}), 400

    try:
        price = float(price)
        stock = int(stock)
    except (ValueError, TypeError):
        return jsonify({"error": "Price must be a number and stock must be an integer"}), 400

    if price < 0 or stock < 0:
        return jsonify({"error": "Price and stock must be positive numbers"}), 400

    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category id does not exist"}), 400

    try:
        new_product = Product(
            name=name,
            price=price,
            stock=stock,
            category_id=category_id
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Product created successfully", "data": new_product.to_dict()}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


# -------------------------------------------------------------------
# 2. GET - /products --> List all products
# -------------------------------------------------------------------
@products_bp.route('', methods=['GET'])
def list_all_products():
    try:
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products]), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500


# -------------------------------------------------------------------
# 3. GET - /products/<id> --> Get a specific product
# -------------------------------------------------------------------
@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"message": "Product not found", "status": "error"}), 404
        return jsonify(product.to_dict()), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500
    
# -------------------------------------------------------------------
# 4. PUT - /products/<id> --> Update a specific product
# -------------------------------------------------------------------
@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found", "status": "error"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    updated = False

    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        if len(name) < 3:
            return jsonify({"error": "Name must be at least 3 characters"}), 400
        product.name = name
        updated = True

    if 'price' in data:
        try:
            price = float(data['price'])
        except (ValueError, TypeError):
            return jsonify({"error": "Price must be a valid number"}), 400
        if price < 0:
            return jsonify({"error": "Price must be a positive number"}), 400
        product.price = price
        updated = True

    if 'stock' in data:
        try:
            stock = int(data['stock'])
        except (ValueError, TypeError):
            return jsonify({"error": "Stock must be a valid integer"}), 400
        if stock < 0:
            return jsonify({"error": "Stock must be a non-negative integer"}), 400
        product.stock = stock
        updated = True

    if 'category_id' in data:
        try:
            category_id = int(data['category_id'])
        except (ValueError, TypeError):
            return jsonify({"error": "Category ID must be a valid integer"}), 400
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category id does not exist"}), 400
        product.category_id = category_id
        updated = True

    if not updated:
        return jsonify({"message": "No fields to update", "data": product.to_dict()}), 200

    try:
        db.session.commit()
        return jsonify({"message": "Product updated successfully", "data": product.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category id does not exist or data conflict"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


# -------------------------------------------------------------------
# 5. DELETE - /products/<id> --> Delete a product (if no order exists)
# -------------------------------------------------------------------
@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found", "status": "error"}), 404

    # Cek apakah produk sedang digunakan di order_items
    exists = db.session.query(order_items).filter(order_items.c.product_id == product_id).first()
    if exists:
        return jsonify({
            "error": "Cannot delete product: active orders exist",
            "status": "error"
        }), 409

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500