from flask import Flask
from flask_migrate import Migrate
from models import User, Category, Product, Order
from routes import users_bp, products_bp
from utils import db


def init_app():
    print("initializing Flask App...")
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://heraklosadiafora:root@localhost:5432/revoshop_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    migrate = Migrate(app, db) # Initialize Flask-Migrate with the app and db

    print("Registering blueprints...")
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)

    print("Flask app initialized successfully.")
    return app

app = init_app()