from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.services.order_service import OrderService
from app.schemas.order_schema import OrderCreateSchema, OrderUpdateSchema
from app.utils.response_builder import success_response, error_response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import db 

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


# ================================================================
# POST /orders - Place order (JWT Required)
# ================================================================
@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """
    Register a new order
    ---
    tags:
      - Order
    summary: Create a new order
    security: 
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - items
          properties:
            items:
              type: array
              items:
                type: object
                required:
                  - product_id
                  - quantity
                properties:
                  product_id:
                    type: integer
                    description: ID of the product to order
                    example: 1
                  quantity:
                    type: integer
                    description: Quantity of the product
                    example: 3
    responses:
      201:
        description: Order created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                message:
                  type: string
                  example: "Order placed successfully"
                order_id:
                  type: integer
                  example: 123
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid input data"
      404:
        description: Product not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Product not found"
      409:
        description: Data conflict (e.g., duplicate entry or invalid reference)
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Data conflict"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Internal server error"
    """
    try:
        user_id = int(get_jwt_identity())
        data = OrderCreateSchema().load(request.get_json())
        order = OrderService.create_order(user_id, data['items'])
        return success_response({"message": "Order placed successfully", "order_id": order.id}, 201)
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 404)
    except IntegrityError as e:
        db.session.rollback()  
        return error_response("Data conflict (duplicate entry or invalid reference)", 409)
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database system error", 500)
    except Exception as e:
        db.session.rollback()
        return error_response("Internal server error", 500)


# ================================================================
# GET /orders - List all orders for current user (JWT Required)
# ================================================================
@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """
    Get all orders
    ---
    tags:
      - Order
    summary: Get all orders for the authenticated user
    security:
      - Bearer: []
    responses:
      200:
        description: A list of orders for the authenticated user
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  user_id:
                    type: integer
                  status:
                    type: string
                  total_price:
                    type: number
                  created_at:
                    type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Internal server error"
    """
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
    """
    Get order by ID
    ---
    tags:
      - Order
    summary: Get a specific order by ID with its items
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        required: true
        type: integer
        description: ID of the order to retrieve
    responses:
      200:
        description: Order data with items
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 123
            user_id:
              type: integer
              example: 456
            status:
              type: string
              example: "pending"
            total_price:
              type: number
              format: float
              example: 99.99
            created_at:
              type: string
              format: date-time
              example: "2023-01-01T00:00:00Z"
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 789
                  quantity:
                    type: integer
                    example: 2
                  unit_price:
                    type: number
                    format: float
                    example: 49.99
                  subtotal:
                    type: number
                    format: float
                    example: 99.98
      403:
        description: Forbidden - User not authorized to access this order
        schema:
          type: object
          properties:
            error:
              type: string
              example: "You are not authorized to access this order"
      404:
        description: Order not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Order not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Internal server error"
    """
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
    """
    Delete order by ID
    ---
    tags:
      - Order
    summary: Delete a specific order
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        required: true
        type: integer
        description: ID of the order to delete
    responses:
      200:
        description: Order deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Order deleted successfully"
      403:
        description: Forbidden - User not authorized to delete this order
        schema:
          type: object
          properties:
            error:
              type: string
              example: "You are not authorized to delete this order"
      404:
        description: Order not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Order not found"
      409:
        description: Data conflict (e.g., foreign key constraint violation)
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Data conflict"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Internal server error"
    """
    try:
        user_id = int(get_jwt_identity())
        OrderService.delete_order(order_id, user_id)
        return success_response({"message": "Order deleted successfully"}, 200)
    except ValueError as e:
        return error_response(str(e), 404)
    except PermissionError as e:
        return error_response(str(e), 403)
    except IntegrityError as e:
        db.session.rollback()  
        return error_response("Data conflict (duplicate entry or invalid reference)", 409)
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database system error", 500)
    except Exception as e:
        db.session.rollback()
        return error_response("Internal server error", 500)

# ================================================================
# PUT /orders/<id> - Update status order (JWT Required + Authorization check)
# ================================================================
@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    """
    Update order status by ID
    ---
    tags:
      - Order
    summary: Update status of a specific order
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        required: true
        type: integer
        description: ID of the order to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              description: New status of the order
              example: "shipped"
    responses:
      200:
        description: Order status updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                message:
                  type: string
                  example: "Order status updated successfully"
                order:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 123
                    user_id:
                      type: integer
                      example: 456
                    status:
                      type: string
                      example: "shipped"
                    total_price:
                      type: number
                      format: float
                      example: 99.99
                    created_at:
                      type: string
                      format: date-time
                      example: "2023-01-01T00:00:00Z"
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid input data"
      403:
        description: Forbidden - User not authorized to update this order
        schema:
          type: object
          properties:
            error:
              type: string
              example: "You are not authorized to update this order"
      404:
        description: Order not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Order not found"
      409:
        description: Data conflict (e.g., duplicate entry or invalid reference)
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Data conflict"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Internal server error"
    """
    try:
        user_id = int(get_jwt_identity())
        data = OrderUpdateSchema().load(request.get_json())
        order = OrderService.update_order(order_id, user_id, data)
        return success_response({"message": "Order status updated successfully", "order": order.to_dict()}, 200)
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 404)
    except IntegrityError as e:
        db.session.rollback()  
        return error_response("Data conflict (duplicate entry or invalid reference)", 409)
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database system error", 500)
    except Exception as e:
        db.session.rollback()
        return error_response("Internal server error", 500)