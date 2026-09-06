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
    """
    Register a new category
    ---
    tags:
      - Category
    summary: Create a new category
    security: 
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - category_name
          properties:
            category_name:
              type: string
              example: "Electronics"
    responses:
      201:
        description: Category created successfully
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
                  example: 1
                category_name:
                  type: string
                  example: "Electronics"
      400:
        description: Bad request - Validation error
      409:
        description: Conflict - Data conflict (duplicate entry or invalid reference)
      500:
        description: Internal server error
    """
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
    """
    Get all categories
    ---
    tags:
      - Category
    summary: Get all categories
    responses:
      200:
        description: List of categories
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
                    example: 1
                  category_name:
                    type: string
                    example: "Electronics"
      500:
        description: Internal server error
    """
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
    """
    Get category by ID
    ---
    tags:
      - Category
    summary: Get category by ID
    parameters:
      - name: category_id
        in: path
        required: true
        description: ID of the category to retrieve
    responses:
      200:
        description: Category data
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
                  example: 1
                category_name:
                  type: string
                  example: "Electronics"
                products:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      name:
                        type: string
                        example: "Smartphone"
                      price:
                        type: number
                        format: float
                        example: 699.99
      404:
        description: Category not found
      500:
        description: Internal server error
    """
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
    """
    Update category by ID
    ---
    tags:
      - Category
    summary: Update a category
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        required: true
        description: ID of the category to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - category_name
          properties:
            category_name:
              type: string
              example: "Electronics"
    responses:
      200:
        description: Category updated successfully
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
                  example: 1
                category_name:
                  type: string
                  example: "Electronics"
      400:
        description: Bad request - Validation error
      409:
        description: Conflict - Data conflict (duplicate entry or invalid reference)
      500:
        description: Internal server error
    """
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
    """
    Delete category by ID
    ---
    tags:
      - Category
    summary: Delete a category by ID
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        required: true
        description: ID of the category to delete
    responses:
      200:
        description: Category deleted successfully
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
                  example: "Category deleted successfully"
      404:
        description: Category not found
      409:
        description: Conflict - Cannot delete category with existing products
      500:
        description: Internal server error
    """
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