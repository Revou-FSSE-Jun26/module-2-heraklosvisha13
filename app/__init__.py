from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from app.models import db
from app.utils.response_builder import register_error_handlers

# Import Blueprint dari api
from app.api.auth import auth_bp, users_bp
from app.api.products import products_bp
from app.api.categories import categories_bp
from app.api.orders import orders_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inisialisasi Ekstensi
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Register Blueprint (Endpoint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(main_bp)

    # Register Error Handler
    register_error_handlers(app)

    return app