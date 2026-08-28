# tests/test_products.py
# ============================================================
# UNIT TESTING: PRODUCT CRUD + DELETION GUARD (409 Conflict)
# ============================================================

def get_id_from_response(resp):
    """Ambil ID dari response (baik yang pakai wrapper 'data' maupun langsung)."""
    if 'data' in resp.json:
        return resp.json['data']['id']
    elif 'id' in resp.json:
        return resp.json['id']
    else:
        raise KeyError(f"ID not found in response: {resp.json}")


def test_create_product_success(client, auth_token):
    """POST /products -> Data benar -> 201 Created (Happy Path)."""
    # 1. Buat category (perlu token)
    cat_res = client.post('/categories',
        json={'category_name': 'Electronics'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(cat_res)

    # 2. Buat produk
    res = client.post('/products',
        json={
            'name': 'Laptop',
            'price': 1000,
            'stock': 10,
            'category_id': cat_id
        },
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 201
    if 'data' in res.json:
        assert res.json['data']['name'] == 'Laptop'
    else:
        assert res.json['name'] == 'Laptop'


def test_create_product_negative_price(client, auth_token):
    """POST /products -> Price negatif -> 400 Bad Request (Error Case)."""
    # 1. Buat category (perlu token)
    cat_res = client.post('/categories',
        json={'category_name': 'Gadget'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(cat_res)

    # 2. Buat produk dengan harga negatif
    res = client.post('/products',
        json={
            'name': 'Laptop',
            'price': -100,
            'stock': 10,
            'category_id': cat_id
        },
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 400
    if 'message' in res.json:
        error_msg = str(res.json['message'])
    else:
        error_msg = str(res.json)
    assert 'greater than or equal to 0' in error_msg or '>= 0' in error_msg


def test_get_products_public(client):
    """GET /products -> Public, tanpa token -> 200 OK (Happy Path)."""
    res = client.get('/products')
    assert res.status_code == 200
    if 'data' in res.json:
        assert isinstance(res.json['data'], list)
    else:
        assert isinstance(res.json, list)


def test_get_product_not_found(client):
    """GET /products/999 -> ID tidak ada -> 404 Not Found (Error Case)."""
    res = client.get('/products/999')
    assert res.status_code == 404
    if 'message' in res.json:
        assert 'not found' in res.json['message'].lower()
    else:
        assert 'not found' in str(res.json).lower()


def test_delete_product_blocked_by_order(client, auth_token):
    """
    DELETE /products/<id> -> Produk sudah dipesan -> 409 Conflict.
    INI ADALAH BUKTI DELETION GUARD UNTUK PRODUCT DI TEST OTOMATIS!
    """
    # 1. Buat category (perlu token)
    cat_res = client.post('/categories',
        json={'category_name': 'TestCat'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(cat_res)

    # 2. Buat produk (perlu token)
    prod_res = client.post('/products',
        json={
            'name': 'Test Product',
            'price': 100,
            'stock': 5,
            'category_id': cat_id
        },
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    product_id = get_id_from_response(prod_res)

    # 3. Buat order untuk produk tersebut (perlu token)
    order_res = client.post('/orders',
        json={'items': [{'product_id': product_id, 'quantity': 1}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert order_res.status_code == 201

    # 4. Coba hapus produk (harus 409 Conflict)
    res = client.delete(f'/products/{product_id}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 409
    if 'message' in res.json:
        assert 'active orders exist' in res.json['message'].lower()
    else:
        assert 'active orders exist' in str(res.json).lower()