# RevoShop — E-Commerce REST API

## Deskripsi

Proyek ini adalah REST API untuk sistem e-commerce **RevoShop**, dibangun dengan **Flask**, **SQLAlchemy**, dan **PostgreSQL**. API mendukung autentikasi berbasis **JWT**, manajemen produk & kategori, serta pemesanan (orders). Schema database dikelola dengan **Flask-Migrate (Alembic)**.

Arsitektur disusun secara berlapis (layered): **API (routes) → Service (business logic) → Model (ORM)**, dengan validasi input menggunakan **Marshmallow**.

---

## Tech Stack

| Teknologi          | Keterangan                              |
| ------------------ | --------------------------------------- |
| Python 3           | Bahasa pemrograman                      |
| Flask              | Web framework                           |
| Flask-SQLAlchemy   | ORM untuk database                      |
| Flask-Migrate      | Database migration (Alembic)            |
| Flask-JWT-Extended | Autentikasi berbasis JWT                |
| Marshmallow        | Validasi & serialisasi request/response |
| PostgreSQL         | Database relasional                     |
| Werkzeug           | Password hashing                        |
| pytest             | Automated testing                       |
| Locust             | Load testing                            |

---

## Struktur File

```text
.
├── run.py                      # Entry point (create_app + app.run)
├── config.py                   # Config & TestingConfig (baca dari .env)
├── requirements.txt            # Python dependencies
├── locustfile.py               # Skenario load testing
├── app/
│   ├── __init__.py             # Application factory: create_app()
│   ├── api/                    # Route handlers (Blueprint)
│   │   ├── auth.py             # /auth/login, /users (register)
│   │   ├── products.py         # /products
│   │   ├── categories.py       # /categories
│   │   └── orders.py           # /orders
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── order.py            # Order + order_items (association table)
│   ├── schemas/                # Marshmallow schemas (validasi)
│   ├── services/               # Business logic
│   └── utils/
│       └── response_builder.py # Format response & error handler
├── migrations/                 # Flask-Migrate / Alembic
│   └── versions/
├── tests/                      # pytest (auth, products, categories)
│   └── conftest.py
├── docs/                       # Screenshot & ERD
│   └── ERD_revoshop.png
├── .env.example
├── .gitignore
└── README.md
```

---

## Database Models

Database terdiri dari 5 tabel:

| Tabel         | Deskripsi                                       |
| ------------- | ----------------------------------------------- |
| `users`       | Data pengguna (username, email, password, role) |
| `categories`  | Kategori produk                                 |
| `products`    | Data produk (nama, harga, stok, kategori)       |
| `orders`      | Data pesanan pengguna                           |
| `order_items` | Association table antara orders dan products    |

Relasi:

- Satu `category` memiliki banyak `products`
- Satu `user` memiliki banyak `orders`
- `orders` dan `products` terhubung many-to-many melalui `order_items`

ERD tersedia di `docs/ERD_revoshop.png`.

---

## Setup & Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd module-2-heraklosvisha13
```

### 2. Buat Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL

Pastikan PostgreSQL berjalan, lalu buat dua database — satu untuk aplikasi dan satu untuk testing:

```sql
CREATE DATABASE revoshop_db;
CREATE DATABASE revoshop_test_db;
```

### 5. Konfigurasi Environment

Salin `.env.example` menjadi `.env`, lalu sesuaikan nilainya:

```bash
cp .env.example .env
```

Variabel yang dibaca aplikasi (lihat `config.py`):

| Variabel               | Keterangan                                              |
| ---------------------- | ------------------------------------------------------- |
| `DATABASE_URL`         | Connection string database utama                       |
| `DATABASE_TESTING_URL` | Connection string database testing (dipakai saat pytest)|
| `SECRET_KEY`           | Secret key Flask                                        |
| `JWT_SECRET_KEY`       | Secret key untuk signing JWT                            |
| `JWT_EXPIRATION`       | Masa berlaku token (detik), default `3600`              |
| `DEBUG`                | `True` / `False`                                        |
| `LOAD_TEST_USERNAME`   | Username user untuk load testing (Locust)               |
| `LOAD_TEST_PASSWORD`   | Password plaintext user tersebut untuk Locust           |

Contoh:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/revoshop_db
DATABASE_TESTING_URL=postgresql://user:password@localhost:5432/revoshop_test_db
SECRET_KEY=change_me
JWT_SECRET_KEY=change_me_too
JWT_EXPIRATION=3600
DEBUG=True
LOAD_TEST_USERNAME=andi_cobra
LOAD_TEST_PASSWORD=password123
```

> Catatan: `LOAD_TEST_PASSWORD` harus berupa **password plaintext asli** dari user tersebut, bukan nilai `password_hash` yang tersimpan di database. Login memverifikasi plaintext terhadap hash, jadi mengisi nilai hash akan selalu gagal (401).

### 6. Jalankan Migration

```bash
flask db upgrade
```

---

## Menjalankan Aplikasi

```bash
python run.py
```

atau:

```bash
flask run
```

Server berjalan di `http://127.0.0.1:5000`.

---

## Autentikasi (JWT)

Endpoint yang ditandai **JWT** memerlukan header:

```
Authorization: Bearer <token>
```

Token diperoleh dari `POST /auth/login`. Alur umum: register user (`POST /users`) → login (`POST /auth/login`) → gunakan token pada endpoint yang butuh autentikasi.

---

## API Endpoints

### Auth & Users

| Method | Endpoint      | Auth   | Deskripsi                         |
| ------ | ------------- | ------ | --------------------------------- |
| POST   | `/users`      | Public | Registrasi user baru              |
| POST   | `/auth/login` | Public | Login, mengembalikan JWT token    |

### Products

| Method | Endpoint          | Auth   | Deskripsi                                    |
| ------ | ----------------- | ------ | -------------------------------------------- |
| GET    | `/products`       | Public | Daftar semua produk                          |
| GET    | `/products/<id>`  | Public | Detail produk by ID                          |
| POST   | `/products`       | JWT    | Buat produk baru                             |
| PUT    | `/products/<id>`  | JWT    | Update produk                                |
| DELETE | `/products/<id>`  | JWT    | Hapus produk (ditolak jika ada order aktif)  |

### Categories

| Method | Endpoint            | Auth   | Deskripsi                                   |
| ------ | ------------------- | ------ | ------------------------------------------- |
| GET    | `/categories`       | Public | Daftar semua kategori                       |
| GET    | `/categories/<id>`  | Public | Detail kategori beserta produknya           |
| POST   | `/categories`       | JWT    | Buat kategori baru                          |
| PUT    | `/categories/<id>`  | JWT    | Update kategori                             |
| DELETE | `/categories/<id>`  | JWT    | Hapus kategori (ditolak jika ada produk)    |

### Orders

| Method | Endpoint        | Auth | Deskripsi                                        |
| ------ | --------------- | ---- | ------------------------------------------------ |
| POST   | `/orders`       | JWT  | Buat pesanan baru                                |
| GET    | `/orders`       | JWT  | Daftar pesanan milik user yang sedang login      |
| GET    | `/orders/<id>`  | JWT  | Detail pesanan beserta item (hanya milik sendiri)|
| DELETE | `/orders/<id>`  | JWT  | Hapus pesanan (hanya milik sendiri)              |

### Contoh Request — Login

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "andi_cobra", "password": "password123"}'
```

Response:

```json
{
  "status": "success",
  "data": {
    "message": "Login successful",
    "token": "<jwt-token>",
    "user": {
      "id": 4,
      "username": "andi_cobra",
      "email": "andi_cobra@example.com",
      "role": "customer"
    }
  }
}
```

### Contoh Request — Buat Order (JWT)

```bash
curl -X POST http://127.0.0.1:5000/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{"items": [{"product_id": 1, "quantity": 1}]}'
```

> Format response mengikuti pola konsisten: sukses `{"status": "success", "data": ...}`, error `{"status": "error", "message": ...}`.

---

## Database Migration

```bash
# Buat migration baru setelah mengubah model
flask db migrate -m "deskripsi perubahan"

# Terapkan migration ke database
flask db upgrade

# Rollback migration terakhir
flask db downgrade
```

---

## Testing

Testing menggunakan **pytest**. Database yang dipakai adalah `DATABASE_TESTING_URL` (`revoshop_test_db`), terpisah dari database utama sehingga menjalankan test tidak menyentuh data produksi.

```bash
pytest -v -s
```

`tests/conftest.py` membuat app dengan `TestingConfig`, membuat tabel sebelum test, dan menghapusnya setelah selesai. Ada pula guard yang menolak menjalankan test bila URI database bukan database testing.

---

## Load Testing

Load testing menggunakan **Locust** (`locustfile.py`). Skenario: login sekali di `on_start`, lalu mengulang alur GET produk → buat order → GET order.

Pastikan `LOAD_TEST_USERNAME` dan `LOAD_TEST_PASSWORD` di `.env` merujuk ke user yang benar-benar ada dan bisa login (password plaintext, bukan hash).

Jalankan (aplikasi harus running lebih dulu):

```bash
locust -f locustfile.py --host http://127.0.0.1:5000
```

Buka `http://localhost:8089` untuk mengatur jumlah user dan memulai test.

---

## Screenshot

Screenshot pengujian tersedia di folder `docs/`:

- Register user: `Screenshot-post-register-user.png`
- Get user by ID: `Screenshot-get-user-by-id-foundid.png`
- Get all products: `Screenshot-get-products-all.png`
- Get product by ID: `Screenshot-get-products-by-id-found.png`
- Role column added: `Screenshoot-role-column-added.png`

---

## Tujuan Project

Project ini dibuat untuk memahami:

- Membangun REST API dengan Flask dan arsitektur berlapis (API/Service/Model)
- Object-Relational Mapping (ORM) dengan SQLAlchemy
- Autentikasi & otorisasi berbasis JWT
- Validasi input dengan Marshmallow
- Database migration dengan Flask-Migrate / Alembic
- Password hashing dengan Werkzeug
- Relasi antar tabel (One-to-Many, Many-to-Many)
- Automated testing dengan pytest (database testing terpisah)
- Load testing dengan Locust
- PostgreSQL sebagai production database
