from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "RevoShop API",
        "version": "1.0.0",
        "status": "running",
        }
    }), 200