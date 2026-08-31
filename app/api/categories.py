from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services.category_service import CategoryService
from app.schemas.category_schema import CategoryCreateSchema, CategoryUpdateSchema
from app.utils.response_builder import success_response, error_response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import db 

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


# ================================================================
# POST /categories - Create category (JWT Required)
# ================================================================
@categories_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    try:
        data = CategoryCreateSchema().load(request.get_json())
        category = CategoryService.create_category(data)
        return success_response(category.to_dict(), 201)
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
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


# ================================================================
# GET /categories - List all categories (PUBLIC)
# ================================================================
@categories_bp.route('', methods=['GET'])
def get_categories():
    try:
        categories = CategoryService.get_all_categories()
        return success_response([c.to_dict() for c in categories], 200)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# GET /categories/<id> - Get category with products (PUBLIC)
# ================================================================
@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = CategoryService.get_category_by_id(category_id)
        return success_response(category.to_dict(include_products=True), 200)
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# PUT /categories/<id> - Update category (JWT Required)
# ================================================================
@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    try:
        data = CategoryUpdateSchema().load(request.get_json())
        category = CategoryService.update_category(category_id, data)
        return success_response(category.to_dict(), 200)
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
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


# ================================================================
# DELETE /categories/<id> - Delete category (JWT Required + Block if products exist)
# ================================================================
@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    try:
        CategoryService.delete_category(category_id)
        return success_response({"message": "Category deleted successfully"}, 200)
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