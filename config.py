import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_EXPIRATION', 3600))
    )
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TESTING_URL')


# ====================
# KONFIGURASI SWAGGER
# ====================

SWAGGER_TEMPLATE = {
    "info": {
        "title": "Revoshop API",
        "description": "Dokumentasi API untuk aplikasi E-Commerce Revoshop",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Enter: **Bearer <your-token>**"
        }
    },
    "security": [
        {"Bearer": []} 
    ]
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}