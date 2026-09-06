from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.auth_service import AuthService
from app.schemas.auth_schema import RegisterSchema, LoginSchema
from app.utils.response_builder import success_response, error_response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import db 

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
users_bp = Blueprint('users', __name__, url_prefix='/users')


# ================================================================
# POST /auth/login - Login user
# ================================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login and get a JWT token
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "budi"
            password:
              type: string
              example: "hashed_password_1"
    responses:
      200:
        description: Login successful, returns JWT token
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
              properties:
                message:
                  type: string
                token:
                  type: string
                user:
                  type: object
      400:
        description: Validation error
      401:
        description: Invalid credentials
    """
    try:
        data = LoginSchema().load(request.get_json())
        token, user = AuthService.login_user(data)
        return success_response({
            "message": "Login successful",
            "token": token,
            "user": user.to_dict()
        }, 200)
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 401)
    except Exception:
        return error_response("Internal server error", 500)


# ================================================================
# POST /users - Register new user
# ================================================================
@users_bp.route('', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    summary: Create a new user account
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: "joko"
            email:
              type: string
              format: email
              example: "joko@example.com"
            password:
              type: string
              example: "password_example_1"
    responses:
      201:
        description: User created successfully
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
                  example: "User created successfully"
                user:
                  type: object
                  properties:
                    id:
                      type: integer
                    username:
                      type: string
                    email:
                      type: string
                    created_at:
                      type: string
      400:
        description: Validation error (missing field or invalid format)
      409:
        description: Username or email already exists
      500:
        description: Internal server error
    """
    try:
        data = RegisterSchema().load(request.get_json())
        user = AuthService.register_user(data)
        return success_response({
            "message": "User created successfully",
            "user": user.to_dict()
        }, 201)
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