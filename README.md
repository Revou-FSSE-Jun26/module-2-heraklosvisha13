# RevoShop — E-Commerce REST API

REST API untuk sistem e-commerce **RevoShop**, dibangun dengan **Flask**, **SQLAlchemy**, dan **PostgreSQL**. API menyediakan autentikasi berbasis **JWT**, manajemen produk & kategori, serta pemesanan (orders). Skema database dikelola dengan **Flask-Migrate (Alembic)** dan validasi input memakai **Marshmallow**.

Kode disusun berlapis agar mudah dirawat: **API (routes) → Service (business logic) → Model (ORM)**.

> 🚀 **Live Demo:** [https://module-2-heraklosvisha13.onrender.com](https://module-2-heraklosvisha13.onrender.com)

---

## Daftar Isi

1. [Tech Stack](#1-tech-stack)
2. [Arsitektur & Struktur File](#2-arsitektur--struktur-file)
3. [Database Models](#3-database-models)
4. [Menjalankan di Lokal](#4-menjalankan-di-lokal)
5. [Alur Penggunaan API (Quick Start)](#5-alur-penggunaan-api-quick-start)
6. [Referensi API Endpoints](#6-referensi-api-endpoints)
7. [Contoh Request](#7-contoh-request)
8. [Database Migration](#8-database-migration)
9. [Deployment (Render + Supabase)](#9-deployment-render--supabase)
10. [Testing & Load Testing](#10-testing--load-testing)
11. [Screenshot / Bukti Pengujian](#11-screenshot--bukti-pengujian)
12. [Tujuan Project](#12-tujuan-project)

---

## 1. Tech Stack

| Teknologi          | Peran                                   |
| ------------------ | --------------------------------------- |
| Python 3           | Bahasa pemrograman                      |
| Flask              | Web framework                           |
| Flask-SQLAlchemy   | ORM untuk database                      |
| Flask-Migrate      | Database migration (Alembic)            |
| Flask-JWT-Extended | Autentikasi berbasis JWT                |
| Marshmallow        | Validasi & serialisasi request/response |
| PostgreSQL         | Database relasional                     |
| Werkzeug           | Password hashing                        |
| Gunicorn           | WSGI server (production)                |
| pytest             | Automated testing                       |
| Locust             | Load testing                            |

---

## 2. Arsitektur & Struktur File

Setiap request mengalir melalui tiga lapisan yang tanggung jawabnya terpisah:

```text
Request ──► API (routes)  ──► Service (business logic) ──► Model (ORM) ──► PostgreSQL
             validasi           aturan bisnis,              query &
             input (schema)     otorisasi                   relasi tabel
```

Struktur folder:

```text
.
├── run.py                      # Entry point (create_app + app.run)
├── config.py                   # Config & TestingConfig (baca dari .env)
├── requirements.txt            # Python dependencies
├── Procfile                    # Perintah start untuk Render (Gunicorn)
├── locustfile.py               # Skenario load testing
├── app/
│   ├── __init__.py             # Application factory: create_app()
│   ├── api/                    # Lapisan 1 — Route handlers (Blueprint)
│   │   ├── auth.py             #   /auth/login, /users (register)
│   │   ├── products.py         #   /products
│   │   ├── categories.py       #   /categories
│   │   └── orders.py           #   /orders
│   ├── schemas/                # Validasi input (Marshmallow)
│   ├── services/               # Lapisan 2 — Business logic
│   ├── models/                 # Lapisan 3 — SQLAlchemy models
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── order.py            #   Order + order_items (association table)
│   └── utils/
│       └── response_builder.py # Format response & error handler
├── migrations/versions/        # Flask-Migrate / Alembic
├── tests/                      # pytest (auth, products, categories)
│   └── conftest.py
├── docs/                       # Screenshot & ERD
│   └── ERD_revoshop.png
├── .env.example
└── README.md
```

---

## 3. Database Models

Database terdiri dari 5 tabel:

| Tabel         | Deskripsi                                        |
| ------------- | ------------------------------------------------ |
| `users`       | Data pengguna (username, email, password, role)  |
| `categories`  | Kategori produk                                  |
| `products`    | Data produk (nama, harga, stok, kategori)        |
| `orders`      | Data pesanan pengguna                            |
| `order_items` | Association table antara `orders` dan `products` |

**Relasi antar tabel:**

- Satu `category` memiliki banyak `products` (one-to-many)
- Satu `user` memiliki banyak `orders` (one-to-many)
- `orders` ↔ `products` many-to-many melalui `order_items`

ERD lengkap: [`docs/ERD_revoshop.png`](docs/ERD_revoshop.png).

---

## 4. Menjalankan di Lokal

Ikuti langkah berikut secara berurutan.

### Langkah 1 — Clone & masuk ke folder

```bash
git clone <repository-url>
cd module-2-heraklosvisha13
```

### Langkah 2 — Virtual environment & dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Langkah 3 — Siapkan database PostgreSQL

Buat dua database terpisah — satu untuk aplikasi, satu khusus testing:

```sql
CREATE DATABASE revoshop_db;
CREATE DATABASE revoshop_test_db;
```

### Langkah 4 — Konfigurasi `.env`

Salin template lalu sesuaikan nilainya:

```bash
cp .env.example .env
```

Variabel yang dibaca aplikasi (lihat `config.py`):

| Variabel               | Keterangan                                               |
| ---------------------- | -------------------------------------------------------- |
| `DATABASE_URL`         | Connection string database utama                        |
| `DATABASE_TESTING_URL` | Connection string database testing (dipakai saat pytest) |
| `SECRET_KEY`           | Secret key Flask                                         |
| `JWT_SECRET_KEY`       | Secret key untuk signing JWT                             |
| `JWT_EXPIRATION`       | Masa berlaku token dalam detik (default `3600`)          |
| `DEBUG`                | `True` / `False`                                         |
| `LOAD_TEST_USERNAME`   | Username user untuk load testing (Locust)                |
| `LOAD_TEST_PASSWORD`   | Password **plaintext** user tersebut untuk Locust        |

Contoh isi `.env`:

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

> **Catatan:** `LOAD_TEST_PASSWORD` harus password **plaintext asli**, bukan nilai `password_hash` di database. Login memverifikasi plaintext terhadap hash, jadi mengisi nilai hash akan selalu gagal (`401`).

### Langkah 5 — Terapkan skema & jalankan

```bash
flask db upgrade        # buat semua tabel dari file migration
python run.py           # atau: flask run
```

Server berjalan di **`http://127.0.0.1:5000`**.

---

## 5. Alur Penggunaan API (Quick Start)

Endpoint dibagi dua: **Public** (bebas diakses) dan **JWT** (butuh token). Alur standar dari nol:

```text
1. Register   →  POST /users        (buat akun, password otomatis di-hash)
2. Login      →  POST /auth/login   (dapat "token" JWT di response)
3. Pakai token → kirim header:  Authorization: Bearer <token>
                 pada semua endpoint bertanda JWT (create order, dsb.)
```

Contoh header untuk endpoint ber-JWT:

```
Authorization: Bearer <token-dari-login>
```

Semua response memakai format konsisten:

- **Sukses:** `{"status": "success", "data": ... }`
- **Error:** `{"status": "error", "message": ... }`

---

## 6. Referensi API Endpoints

Kolom **Auth**: `Public` = tanpa token, `JWT` = wajib header `Authorization: Bearer <token>`.

### Auth & Users

| Method | Endpoint      | Auth   | Deskripsi                      |
| ------ | ------------- | ------ | ------------------------------ |
| POST   | `/users`      | Public | Registrasi user baru           |
| POST   | `/auth/login` | Public | Login, mengembalikan JWT token |

### Products

| Method | Endpoint         | Auth   | Deskripsi                                   |
| ------ | ---------------- | ------ | ------------------------------------------- |
| GET    | `/products`      | Public | Daftar semua produk                         |
| GET    | `/products/<id>` | Public | Detail produk berdasarkan ID                |
| POST   | `/products`      | JWT    | Buat produk baru                            |
| PUT    | `/products/<id>` | JWT    | Update produk                               |
| DELETE | `/products/<id>` | JWT    | Hapus produk (ditolak jika ada order aktif) |

### Categories

| Method | Endpoint           | Auth   | Deskripsi                                |
| ------ | ------------------ | ------ | ---------------------------------------- |
| GET    | `/categories`      | Public | Daftar semua kategori                    |
| GET    | `/categories/<id>` | Public | Detail kategori beserta produknya        |
| POST   | `/categories`      | JWT    | Buat kategori baru                       |
| PUT    | `/categories/<id>` | JWT    | Update kategori                          |
| DELETE | `/categories/<id>` | JWT    | Hapus kategori (ditolak jika ada produk) |

### Orders

| Method | Endpoint       | Auth | Deskripsi                                         |
| ------ | -------------- | ---- | ------------------------------------------------- |
| POST   | `/orders`      | JWT  | Buat pesanan baru                                 |
| GET    | `/orders`      | JWT  | Daftar pesanan milik user yang sedang login       |
| GET    | `/orders/<id>` | JWT  | Detail pesanan beserta item (hanya milik sendiri) |
| DELETE | `/orders/<id>` | JWT  | Hapus pesanan (hanya milik sendiri)               |

---

## 7. Contoh Request

### Register (`POST /users`)

```bash
curl -X POST http://127.0.0.1:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "andi_cobra", "email": "andi_cobra@example.com", "password": "password123"}'
```

### Login (`POST /auth/login`)

```bash
# Lokal
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "andi_cobra", "password": "password123"}'

# Production (Render)
curl -X POST https://module-2-heraklosvisha13.onrender.com/auth/login \
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

### Buat Order (`POST /orders`, butuh JWT)

Salin nilai `token` dari response login ke header `Authorization`:

```bash
curl -X POST http://127.0.0.1:5000/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{"items": [{"product_id": 1, "quantity": 1}]}'
```

---

## 8. Database Migration

```bash
flask db migrate -m "deskripsi perubahan"   # buat migration baru setelah mengubah model
flask db upgrade                            # terapkan migration ke database
flask db downgrade                          # rollback migration terakhir
```

> `flask db migrate` hanya diperlukan saat **model berubah**. Untuk sekadar menerapkan skema yang sudah ada ke database baru, cukup `flask db upgrade`.

---

## 9. Deployment (Render + Supabase)

Aplikasi sudah di-deploy dan dapat diakses publik:

| Item            | Detail                                                  |
| --------------- | ------------------------------------------------------- |
| **Base URL**    | https://module-2-heraklosvisha13.onrender.com           |
| **Platform**    | [Render](https://render.com) — hosting aplikasi Flask   |
| **Database**    | [Supabase](https://supabase.com) — managed PostgreSQL   |
| **WSGI Server** | Gunicorn (`gunicorn --timeout 120 --workers 2 run:app`) |

**Cara kerjanya:** Render menjalankan aplikasi via Gunicorn (sesuai `Procfile`), dan terhubung ke PostgreSQL yang di-host Supabase. Semua kredensial (`DATABASE_URL` Supabase, `SECRET_KEY`, `JWT_SECRET_KEY`, dll.) diset lewat dashboard Render, bukan di file `.env`.

### Menyiapkan skema tabel di Supabase (dijalankan dari lokal)

Skema di Supabase disiapkan **sekali** dari mesin lokal, dengan mengarahkan `DATABASE_URL` sementara ke Supabase, lalu dikembalikan ke lokal:

**1. Arahkan `DATABASE_URL` ke Supabase**

```env
# .env — sementara
DATABASE_URL=postgresql://postgres:<password>@<host>.supabase.co:5432/postgres
```

**2. Terapkan skema**

```bash
flask db upgrade
```

**3. Kembalikan `DATABASE_URL` ke database lokal**

```env
# .env — dikembalikan seperti semula
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/revoshop_db
```

> **Kenapa dikembalikan?** Supaya pengembangan sehari-hari (menjalankan app & test) tetap memakai database lokal dan tidak menyentuh data production. Migration cukup sekali; setelahnya Render langsung terhubung ke Supabase yang skemanya sudah siap.

### Status pengujian production (Postman)

Diuji langsung ke URL Render dan berjalan baik:

| Fitur                | Endpoint           | Status |
| -------------------- | ------------------ | ------ |
| Register user        | `POST /users`      | ✅      |
| Login (JWT)          | `POST /auth/login` | ✅      |
| Listing all products | `GET /products`    | ✅      |

Cek cepat lewat terminal:

```bash
curl https://module-2-heraklosvisha13.onrender.com/products
```

> ⚠️ **Seeding user:** Kolom `password_hash` harus diisi hasil `generate_password_hash` (Werkzeug), **bukan** teks biasa. Seeding user via SQL dengan nilai seperti `'hashed_password_1'` membuat login selalu gagal (`401`). Untuk user yang bisa login, daftarkan lewat `POST /users` agar password di-hash oleh aplikasi. Seeding SQL untuk `categories`, `products`, `orders`, dan `order_items` tetap aman (tidak melibatkan hashing).

> 💤 **Cold start:** Render free tier "tidur" saat idle, jadi request pertama setelah lama menganggur bisa perlu beberapa detik.

---

## 10. Testing & Load Testing

### Automated test (pytest)

Test memakai database `DATABASE_TESTING_URL` (`revoshop_test_db`) yang terpisah dari database utama, sehingga aman dijalankan tanpa menyentuh data produksi.

```bash
pytest -v -s
```

`tests/conftest.py` membuat app dengan `TestingConfig`, membangun tabel sebelum test dan menghapusnya setelah selesai. Ada guard yang menolak menjalankan test bila URI database bukan database testing.

### Load testing (Locust)

Skenario: login sekali di `on_start`, lalu mengulang alur GET produk → buat order → GET order. Pastikan `LOAD_TEST_USERNAME` / `LOAD_TEST_PASSWORD` di `.env` merujuk user yang benar-benar ada (password plaintext, bukan hash).

```bash
# aplikasi harus sudah running lebih dulu
locust -f locustfile.py --host http://127.0.0.1:5000
```

Buka `http://localhost:8089` untuk mengatur jumlah user dan memulai test.

---

## 11. Screenshot / Bukti Pengujian

Semua bukti tersimpan di folder [`docs/`](docs/), disusun mengikuti alur: **infrastruktur → pengujian production → pengujian lokal → struktur database → automated/load test**.

### a. Infrastruktur Deployment

Platform yang menjalankan aplikasi: **Render** meng-host aplikasi Flask, **Supabase** menyediakan PostgreSQL.

![Dashboard Render](docs/Screenshot-Render_dashboard.png)

![Dashboard Supabase](docs/Screenshot-Supabase_dashboard.png)

### b. Pengujian API di Production (URL Render)

Membuktikan aplikasi berjalan end-to-end di cloud, bukan hanya lokal.

**Register (`POST /users`)**

![Register via URL deployment](docs/Screenshot-register-post-render_url.png)

**Login (`POST /auth/login`)**

![Login via URL deployment](docs/Screenshot-auth%3Alogin-post-render_url.png)

![Login via URL deployment (Render + Supabase)](docs/Screenshot-auth%3Alogin-post-render_url-supabase.png)

**Listing all products (`GET /products`)** — data diambil dari database Supabase.

![Get all products via URL deployment](docs/Screenshot-products-get_all-render_url.png)

![Get all products via URL deployment (2)](docs/Screenshot-products-get_all-render_url2.png)

### c. Pengujian API Lokal (Postman)

Pengujian tiap endpoint saat aplikasi jalan di `http://127.0.0.1:5000`, sebagai referensi bentuk request/response dan status code yang diharapkan.

| Modul          | Skenario yang diuji                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------- |
| **Auth/User**  | Register (`201`), Login (`200`), Get user by ID (ditemukan & tidak ditemukan)                   |
| **Products**   | List semua (`200`), get by ID (`200`), create (`201`), update (`200`), delete saat dipakai order (`409`) |
| **Categories** | List semua (`200`), get by ID (`200`), create (`201`), update (`200`), delete saat punya produk (`409`)  |
| **Orders**     | Create (`201`), list semua (`200`), get by ID (`200`), akses order user lain (`403`)            |

File terkait di `docs/`: `Screenshot-user-post-register-201.png`, `Screenshot-user-post-login-200.png`, `Screenshot-product-*`, `Screenshot-category-*`, `Screenshot-order-*`.

### d. Struktur Database

Bukti skema tabel hasil migration, termasuk kolom `role` pada `users` dan association table `order_items`.

- Kolom `role` pada `users`: `Screenshoot-role-column-added.png`
- Struktur tabel `users`: `Screenshot-structur_table-users.png`
- Struktur association table `order_items`: `Screenshot-structur_table-order_items.png`

### e. Automated & Load Testing

- **pytest** — hasil seluruh test: `Screenshot-pytest_result.png`
- **Locust** — hasil load testing: `Screenshot-locust_result.png` (laporan HTML lengkap: `Locust_2026-08-28-22h20_locustfile.py_http___127.0.0.1_5000.html`)

---

## 12. Tujuan Project

Project ini dibuat untuk memahami:

- Membangun REST API dengan Flask dan arsitektur berlapis (API/Service/Model)
- Object-Relational Mapping (ORM) dengan SQLAlchemy
- Autentikasi & otorisasi berbasis JWT
- Validasi input dengan Marshmallow
- Database migration dengan Flask-Migrate / Alembic
- Password hashing dengan Werkzeug
- Relasi antar tabel (one-to-many, many-to-many)
- Automated testing dengan pytest (database testing terpisah)
- Load testing dengan Locust
- Deployment ke Render dengan PostgreSQL (Supabase) sebagai production database
