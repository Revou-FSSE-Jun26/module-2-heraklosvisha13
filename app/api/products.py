from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreateSchema, ProductUpdateSchema
from app.utils.response_builder import success_response, error_response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import db 

products_bp = Blueprint('products', __name__, url_prefix='/products')


# ================================================================
# POST /products - Create product (JWT Required)
# ================================================================
@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """
    Create a new product
    ---
    tags:
      - Product
    summary: Create a new product (JWT required)
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - stock
          properties:
            name:
              type: string
              example: "Laptop Gaming"
            price:
              type: number
              format: float
              example: 15000000
            stock:
              type: integer
              example: 10
            category_id:
              type: integer
              example: 1
    responses:
      201:
        description: Product created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                price:
                  type: number
                stock:
                  type: integer
                category_id:
                  type: integer
      400:
        description: Validation error
      404:
        description: Category not found
      409:
        description: Data conflict (duplicate entry or invalid reference)
      500:
        description: Internal server error
    """
    try:
        data = ProductCreateSchema().load(request.get_json())
        product = ProductService.create_product(data)
        return success_response(product.to_dict(), 201)
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
# GET /products - List all products (PUBLIC)
# ================================================================
@products_bp.route('', methods=['GET'])
def get_products():
    """
    List all products
    ---
    tags:
      - Product
    summary: Get all products (public)
    responses:
      200:
        description: List of products
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
                  name:
                    type: string
                  price:
                    type: number
                  stock:
                    type: integer
                  category_id:
                    type: integer
      500:
        description: Internal server error
    """
    try:
        products = ProductService.get_all_products()
        return success_response([p.to_dict() for p in products], 200)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# GET /products/<id> - Get product by ID (PUBLIC)
# ================================================================
@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get product by ID
    ---
    tags:
      - Product
    summary: Get a single product by ID (public)
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
        example: 1
    responses:
      200:
        description: Product data
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                price:
                  type: number
                stock:
                  type: integer
                category_id:
                  type: integer
      404:
        description: Product not found
      500:
        description: Internal server error
    """
    try:
        product = ProductService.get_product_by_id(product_id)
        return success_response(product.to_dict(), 200)
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# PUT /products/<id> - Update product (JWT Required)
# ================================================================
@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """
    Update product by ID
    ---
    tags:
      - Product
    summary: Update an existing product (JWT required)
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
        example: 1
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Laptop Gaming Pro"
            price:
              type: number
              format: float
              example: 18000000
            stock:
              type: integer
              example: 5
            category_id:
              type: integer
              example: 2
    responses:
      200:
        description: Product updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                price:
                  type: number
                stock:
                  type: integer
                category_id:
                  type: integer
      400:
        description: Validation error
      404:
        description: Product not found
      409:
        description: Data conflict
      500:
        description: Internal server error
    """
    try:
        data = ProductUpdateSchema().load(request.get_json())
        product = ProductService.update_product(product_id, data)
        return success_response(product.to_dict(), 200)
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
# DELETE /products/<id> - Delete product (JWT Required + Block if active orders)
# ================================================================
@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Delete product by ID (blocked if active orders exist)
    ---
    tags:
      - Product
    summary: Delete a product (JWT required, blocked if ordered)
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
        example: 1
    responses:
      200:
        description: Product deleted successfully
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
                  example: "Product deleted successfully"
      404:
        description: Product not found
      409:
        description: Cannot delete product, active orders exist (Deletion Guard)
      500:
        description: Internal server error
    """
    try:
        ProductService.delete_product(product_id)
        return success_response({"message": "Product deleted successfully"}, 200)
    except ValueError as e:
        return error_response(str(e), 404)
    except PermissionError as e:
        return error_response(str(e), 409)
    except IntegrityError as e:
        db.session.rollback()  
        return error_response("Data conflict (duplicate entry or invalid reference)", 409)
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database system error", 500)
    except Exception as e:
        db.session.rollback()
        return error_response("Internal server error", 500)