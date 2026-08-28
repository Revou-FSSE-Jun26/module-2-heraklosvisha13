# tests/test_categories.py
# ============================================================
# UNIT TESTING: CATEGORY CRUD (Happy Path & Error Cases)
# ============================================================

def get_id_from_response(resp):
    """Ambil ID dari response (baik yang pakai wrapper 'data' maupun langsung)."""
    if 'data' in resp.json:
        return resp.json['data']['id']
    elif 'id' in resp.json:
        return resp.json['id']
    else:
        raise KeyError(f"ID not found in response: {resp.json}")


def test_create_category_happy(client, auth_token):
    """POST /categories -> Data benar -> 201 Created (Happy Path)."""
    res = client.post('/categories',
        json={'category_name': 'Electronics'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 201
    if 'data' in res.json:
        assert res.json['data']['category_name'] == 'Electronics'
    else:
        assert res.json['category_name'] == 'Electronics'


def test_create_category_missing_name(client, auth_token):
    """POST /categories -> Tanpa category_name -> 400 Bad Request (Error Case)."""
    res = client.post('/categories',
        json={},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 400
    if 'message' in res.json:
        assert 'required' in str(res.json['message']).lower()
    else:
        assert 'required' in str(res.json).lower()


def test_get_all_categories(client):
    """GET /categories -> Menampilkan semua kategori -> 200 OK (Happy Path)."""
    res = client.get('/categories')
    assert res.status_code == 200
    if 'data' in res.json:
        assert isinstance(res.json['data'], list)
    else:
        assert isinstance(res.json, list)


def test_get_category_by_id_happy(client, auth_token):
    """GET /categories/<id> -> Kategori ditemukan -> 200 OK (Happy Path)."""
    # 1. Buat kategori (perlu token)
    create_res = client.post('/categories',
        json={'category_name': 'Books'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(create_res)

    # 2. GET kategori (public, tanpa token)
    res = client.get(f'/categories/{cat_id}')
    assert res.status_code == 200
    if 'data' in res.json:
        data = res.json['data']
    else:
        data = res.json
    assert data['category_name'] == 'Books'
    assert 'products' in data  # include_products=True


def test_get_category_by_id_not_found(client):
    """GET /categories/999 -> ID tidak ada -> 404 Not Found (Error Case)."""
    res = client.get('/categories/999')
    assert res.status_code == 404
    if 'message' in res.json:
        assert 'not found' in res.json['message'].lower()
    else:
        assert 'not found' in str(res.json).lower()


def test_update_category_happy(client, auth_token):
    """PUT /categories/<id> -> Update nama -> 200 OK (Happy Path)."""
    # 1. Buat kategori
    create_res = client.post('/categories',
        json={'category_name': 'Old Name'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(create_res)

    # 2. Update
    res = client.put(f'/categories/{cat_id}',
        json={'category_name': 'New Name'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 200
    if 'data' in res.json:
        assert res.json['data']['category_name'] == 'New Name'
    else:
        assert res.json['category_name'] == 'New Name'


def test_update_category_empty_name(client, auth_token):
    """PUT /categories/<id> -> Kirim nama kosong -> 400 Bad Request (Error Case)."""
    create_res = client.post('/categories',
        json={'category_name': 'Test'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(create_res)

    res = client.put(f'/categories/{cat_id}',
        json={'category_name': ''},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 400


def test_delete_category_happy(client, auth_token):
    """DELETE /categories/<id> -> Kategori kosong -> 200 OK (Happy Path)."""
    create_res = client.post('/categories',
        json={'category_name': 'ToDelete'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(create_res)

    res = client.delete(f'/categories/{cat_id}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 200
    if 'data' in res.json:
        assert 'deleted' in res.json['data']['message'].lower()
    else:
        assert 'deleted' in str(res.json).lower()


def test_delete_category_blocked_by_products(client, auth_token):
    """
    DELETE /categories/<id> -> Kategori memiliki produk -> 409 Conflict.
    INI ADALAH BUKTI DELETION GUARD UNTUK CATEGORY DI TEST OTOMATIS!
    """
    # 1. Buat kategori (perlu token)
    cat_res = client.post('/categories',
        json={'category_name': 'Gadget'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    cat_id = get_id_from_response(cat_res)

    # 2. Buat produk dengan kategori ini (perlu token)
    prod_res = client.post('/products',
        json={
            'name': 'Smartphone',
            'price': 1000,
            'stock': 10,
            'category_id': cat_id
        },
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert prod_res.status_code == 201  # Pastikan produk berhasil dibuat

    # 3. Coba hapus kategori (harus 409 Conflict)
    res = client.delete(f'/categories/{cat_id}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert res.status_code == 409
    if 'message' in res.json:
        assert 'products still exist' in res.json['message'].lower()
    else:
        assert 'products still exist' in str(res.json).lower()