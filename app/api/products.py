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
    try:
        ProductService.delete_product(product_id)
        return success_response({"message": "Product deleted successfully"}, 200)
    except ValueError as e:
        return error_response(str(e), 404)
    except PermissionError as e:
        return error_response(str(e), 409)  # 409 Conflict!
    except IntegrityError as e:
        db.session.rollback()  
        return error_response("Data conflict (duplicate entry or invalid reference)", 409)
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database system error", 500)
    except Exception as e:
        db.session.rollback()
        return error_response("Internal server error", 500)