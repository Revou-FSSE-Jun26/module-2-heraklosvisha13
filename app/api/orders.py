from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.services.order_service import OrderService
from app.schemas.order_schema import OrderCreateSchema
from app.utils.response_builder import success_response, error_response

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


# ================================================================
# POST /orders - Place order (JWT Required)
# ================================================================
@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    try:
        user_id = int(get_jwt_identity())
        data = OrderCreateSchema().load(request.get_json())
        order = OrderService.create_order(user_id, data['items'])
        return success_response({"message": "Order placed successfully", "order_id": order.id}, 201)
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# GET /orders - List all orders for current user (JWT Required)
# ================================================================
@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    try:
        user_id = int(get_jwt_identity())
        orders = OrderService.get_orders_by_user(user_id)
        return success_response([o.to_dict() for o in orders], 200)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# GET /orders/<id> - Get order with items (JWT Required + Authorization check)
# ================================================================
@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        user_id = int(get_jwt_identity())
        order_data = OrderService.get_order_with_items(order_id, user_id)
        return success_response(order_data, 200)
    except ValueError as e:
        return error_response(str(e), 404)
    except PermissionError as e:
        return error_response(str(e), 403)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# DELETE /orders/<id> - Delete order (JWT Required + Authorization check)
# ================================================================
@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    try:
        user_id = int(get_jwt_identity())
        OrderService.delete_order(order_id, user_id)
        return success_response({"message": "Order deleted successfully"}, 200)
    except ValueError as e:
        return error_response(str(e), 404)
    except PermissionError as e:
        return error_response(str(e), 403)
    except Exception:
        return error_response("Internal server error", 500)