# RevoShop — E-Commerce REST API

## Deskripsi

Proyek ini adalah REST API sederhana untuk sistem e-commerce **RevoShop**, dibangun menggunakan **Flask**, **SQLAlchemy**, dan **PostgreSQL**. Dilengkapi dengan database migration menggunakan **Flask-Migrate (Alembic)**.

---

## Tech Stack

| Teknologi        | Keterangan                          |
| ---------------- | ----------------------------------- |
| Python 3         | Bahasa pemrograman                  |
| Flask            | Web framework                       |
| Flask-SQLAlchemy | ORM untuk database                  |
| Flask-Migrate    | Database migration (Alembic)        |
| PostgreSQL       | Database relasional                 |
| Werkzeug         | Password hashing                    |

---

## Struktur File

```text
.
├── app.py                  # Entry point Flask app
├── models.py               # SQLAlchemy models (User, Category, Product, Order)
├── routes.py               # API route handlers (Blueprint)
├── utils.py                # Shared utilities (db instance)
├── requirements.txt        # Python dependencies
├── migrations/             # Flask-Migrate / Alembic migration files
│   ├── versions/           # Migration scripts
│   ├── env.py
│   └── alembic.ini
├── sql/                    # Raw SQL files (referensi awal)
│   ├── schema.sql
│   ├── seed.sql
│   └── queries.sql
├── docs/                   # Screenshot & ERD
│   └── ERD_revoshop.png
├── .gitignore
└── README.md
```

---

## Database Models

Database `revoshop_db` terdiri dari 5 tabel:

| Tabel         | Deskripsi                                        |
| ------------- | ------------------------------------------------ |
| `users`       | Data pengguna (username, email, password, role)  |
| `categories`  | Kategori produk                                  |
| `products`    | Data produk (nama, harga, stok, kategori)        |
| `orders`      | Data pesanan pengguna                            |
| `order_items` | Association table antara orders dan products     |

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

Pastikan PostgreSQL sudah berjalan, lalu buat database:

```sql
CREATE DATABASE revoshop_db;
```

### 5. Konfigurasi Database

Sesuaikan connection string di `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/revoshop_db'
```

### 6. Jalankan Migration

```bash
flask db upgrade
```

Perintah ini akan membuat semua tabel berdasarkan migration scripts yang ada.

---

## Menjalankan Aplikasi

```bash
flask run
```

Server akan berjalan di `http://127.0.0.1:5000`.

---

## API Endpoints

### Products

| Method | Endpoint           | Deskripsi                  |
| ------ | ------------------ | -------------------------- |
| GET    | `/products`        | Mendapatkan semua produk   |
| GET    | `/products/<id>`   | Mendapatkan produk by ID   |

### Users

| Method | Endpoint          | Deskripsi                   |
| ------ | ----------------- | --------------------------- |
| POST   | `/register`       | Registrasi user baru        |
| GET    | `/users/<id>`     | Mendapatkan user by ID      |

### Contoh Request — Register User

```bash
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'
```

Response:

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "created_at": "2026-08-18T10:00:00"
  }
}
```

---

## Database Migration

Proyek ini menggunakan Flask-Migrate untuk mengelola perubahan schema database.

```bash
# Buat migration baru setelah mengubah models.py
flask db migrate -m "deskripsi perubahan"

# Terapkan migration ke database
flask db upgrade

# Rollback migration terakhir
flask db downgrade
```

Migration yang sudah ada:

1. `6fcb6fd67c68` — Initial tables (tanpa role)
2. `8f6d2ed54ef2` — Menambahkan kolom `role` ke tabel users

---

## Screenshot

Screenshot pengujian API tersedia di folder `docs/`:

- Register user: `Screenshot-post-register-user.png`
- Get user by ID: `Screenshot-get-user-by-id-foundid.png`
- Get all products: `Screenshot-get-products-all.png`
- Get product by ID: `Screenshot-get-products-by-id-found.png`
- Role column added: `Screenshoot-role-column-added.png`

---

## Tujuan Project

Project ini dibuat untuk memahami:

- Membangun REST API dengan Flask
- Object-Relational Mapping (ORM) dengan SQLAlchemy
- Database migration dengan Flask-Migrate / Alembic
- Password hashing dengan Werkzeug
- Relasi antar tabel (One-to-Many, Many-to-Many)
- Blueprint pattern untuk modularisasi routes
- PostgreSQL sebagai production database
