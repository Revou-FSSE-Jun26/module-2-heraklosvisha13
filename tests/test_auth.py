# tests/test_auth.py

def test_register_success(client):
    """POST /users -> Registrasi sukses -> 201 Created."""
    res = client.post('/users', json={
        'username': 'joko',
        'email': 'joko@test.com',
        'password': '123456'
    })
    assert res.status_code == 201
    assert res.json['data']['user']['username'] == 'joko'

def test_register_missing_field(client):
    """POST /users -> Tanpa email -> 400 Bad Request."""
    res = client.post('/users', json={
        'username': 'joko',
        'password': '123456'
    })
    assert res.status_code == 400
    assert 'email' in str(res.json['message'])

def test_login_success(client):
    """POST /auth/login -> Login benar -> 200 OK + Token."""
    res = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'test123'
    })
    assert res.status_code == 200
    assert 'token' in res.json['data']

def test_login_invalid_password(client):
    """POST /auth/login -> Password salah -> 401 Unauthorized."""
    res = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'wrong'
    })
    assert res.status_code == 401