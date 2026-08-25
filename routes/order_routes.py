# ORDER ROUTES:
# 1. POST   - /orders          --> Place a new order (logged-in user)
# 2. GET    - /orders          --> List all orders of current user
# 3. GET    - /orders/<id>     --> View specific order with items
# 4. DELETE - /orders/<id>     --> Delete an order (owner only)

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, Order, Product, order_items
from flask_jwt_extended import jwt_required, get_jwt_identity

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


# -------------------------------------------------------------------
# 1. POST - Create a new order
# -------------------------------------------------------------------
@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    # Ambil user_id dari token JWT
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity in token"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Validasi items
    if 'items' not in data or not data['items']:
        return jsonify({"error": "items is required"}), 400
    if not isinstance(data['items'], list) or len(data['items']) == 0:
        return jsonify({"error": "Items must be a non-empty list"}), 400

    total_price = 0
    order_items_data = []

    # Loop setiap item untuk validasi dan kalkulasi
    for idx, item in enumerate(data['items']):
        # Validasi field per item
        if 'product_id' not in item or not item['product_id']:
            return jsonify({"error": f"Item {idx}: product_id is required"}), 400
        if 'quantity' not in item or item['quantity'] is None:
            return jsonify({"error": f"Item {idx}: quantity is required"}), 400

        # Validasi product_id sebagai integer
        try:
            product_id = int(item['product_id'])
        except (TypeError, ValueError):
            return jsonify({"error": f"Item {idx}: product_id must be an integer"}), 400

        # Validasi quantity
        try:
            quantity = int(item['quantity'])
        except (TypeError, ValueError):
            return jsonify({"error": f"Item {idx}: quantity must be a valid integer"}), 400
        if quantity <= 0:
            return jsonify({"error": f"Item {idx}: quantity must be > 0"}), 400

        # Cek produk ada
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": f"Item {idx}: Product with id {product_id} not found"}), 404

        # Cek stok
        if product.stock < quantity:
            return jsonify({
                "error": f"Item {idx}: Insufficient stock for '{product.name}'. Available: {product.stock}"
            }), 400

        # Kurangi stok dan hitung total
        product.stock -= quantity
        total_price += product.price * quantity
        order_items_data.append({
            "product_id": product.id,
            "quantity": quantity,
            "unit_price": float(product.price)
        })

    # Simpan ke database (dalam transaksi)
    try:
        # Buat order dengan status 'pending' (lebih realistis)
        order = Order(user_id=user_id, total_price=total_price, status='pending')
        db.session.add(order)
        db.session.flush()  # agar order.id tersedia

        # Insert order items (gunakan Core)
        for item in order_items_data:
            db.session.execute(order_items.insert().values(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            ))

        db.session.commit()
        return jsonify({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total_price": total_price
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        # Misal foreign key constraint gagal (user_id tidak valid)
        return jsonify({"error": "Data integrity error, please check your input"}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


# -------------------------------------------------------------------
# 2. GET - List all orders for current user
# -------------------------------------------------------------------
@orders_bp.route('', methods=['GET'])
@jwt_required()
def list_orders():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity in token"}), 400

    try:
        orders = Order.query.filter_by(user_id=user_id).all()
        return jsonify([order.to_dict() for order in orders]), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


# -------------------------------------------------------------------
# 3. GET - View specific order with its items (owner only)
# -------------------------------------------------------------------
@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity in token"}), 400

    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"message": "Order not found", "status": "error"}), 404

        # Otorisasi: hanya pemilik order yang boleh melihat
        if order.user_id != user_id:
            return jsonify({"error": "Forbidden: You are not the owner of this order"}), 403

        # Ambil detail items (dengan Core Table)
        items = []
        # Ambil semua item dari order_items berdasarkan order_id
        stmt = order_items.select().where(order_items.c.order_id == order_id)
        result = db.session.execute(stmt).fetchall()
        for row in result:
            # row adalah tuple: (order_id, product_id, quantity, unit_price)
            product = Product.query.get(row.product_id)
            if product:
                items.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": row.quantity,
                    "unit_price": float(row.unit_price),
                    "subtotal": float(row.quantity * row.unit_price)
                })
            else:
                # Jika produk sudah dihapus, tetap tampilkan data historis
                items.append({
                    "product_id": row.product_id,
                    "product_name": "Deleted Product",
                    "quantity": row.quantity,
                    "unit_price": float(row.unit_price),
                    "subtotal": float(row.quantity * row.unit_price)
                })

        return jsonify({
            "id": order.id,
            "user_id": order.user_id,
            "total_price": float(order.total_price),
            "status": order.status,
            "created_at": order.created_at,
            "items": items
        }), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


# -------------------------------------------------------------------
# 4. DELETE - Delete an order (owner only) + cascade delete items
# -------------------------------------------------------------------
@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity in token"}), 400

    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"message": "Order not found", "status": "error"}), 404

        # Otorisasi
        if order.user_id != user_id:
            return jsonify({"error": "Forbidden: You are not the owner of this order"}), 403

        # Hapus semua item terkait (karena tidak ada cascade di Core)
        db.session.execute(order_items.delete().where(order_items.c.order_id == order_id))

        # Hapus order
        db.session.delete(order)
        db.session.commit()

        return jsonify({"message": "Order deleted successfully", "status": "success"}), 200

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Data integrity error, cannot delete order"}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database system error occurred"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500