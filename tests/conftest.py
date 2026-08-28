# tests/conftest.py
import pytest
from app import create_app
from app.models import db
from app.models.user import User
from werkzeug.security import generate_password_hash
from config import TestingConfig

@pytest.fixture
def client():
    # Pass TestingConfig BEFORE extensions bind to the DB engine,
    # so SQLAlchemy connects to revoshop_test_db, not revoshop_db.
    app = create_app(TestingConfig)
    app.config['TESTING'] = True

    # Safety guard: refuse to run tests against the main database.
    assert 'test' in app.config['SQLALCHEMY_DATABASE_URI'], (
        "Refusing to run tests: SQLALCHEMY_DATABASE_URI is not a test database "
        f"({app.config['SQLALCHEMY_DATABASE_URI']})"
    )

    with app.test_client() as client:
        with app.app_context():
            print(f"\n🔍 [VERIFICATION] Pytest is connected to: {app.config['SQLALCHEMY_DATABASE_URI']}")
            db.create_all()
            user = User(
                username='testuser',
                email='test@test.com',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()  # <-- Sekarang ini hanya menghapus revoshop_test_db

@pytest.fixture
def auth_token(client):
    res = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'test123'
    })
    return res.json['data']['token']