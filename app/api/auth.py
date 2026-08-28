from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.auth_service import AuthService
from app.schemas.auth_schema import RegisterSchema, LoginSchema
from app.utils.response_builder import success_response, error_response

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
users_bp = Blueprint('users', __name__, url_prefix='/users')


# ================================================================
# POST /auth/login - Login user
# ================================================================
@auth_bp.route('/login', methods=['POST'])
def login():
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
    except Exception:
        return error_response("Internal server error", 500)