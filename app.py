from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import users_bp, products_bp


def init_app():
    print("initializing Flask App...")
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Set up database
    db.init_app(app)

    # Set up Flask-migrate
    migrate = Migrate(app, db) # Initialize Flask-Migrate with the app and db

    # Set up JWT
    jwt = JWTManager(app)

    # Register blueprints
    print("Registering blueprints...")
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(orders_bp)

    print("Flask app initialized successfully.")
    return app

app = init_app()