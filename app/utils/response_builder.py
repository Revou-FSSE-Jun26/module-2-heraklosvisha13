from flask import jsonify

def success_response(data, status=200):
    return jsonify({"status": "success", "data": data}), status

def error_response(message, status):
    return jsonify({"status": "error", "message": message}), status

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500