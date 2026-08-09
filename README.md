# 🛒 RevoShop — Database E-Commerce

## 📌 Deskripsi

Proyek ini adalah database sederhana untuk sistem e-commerce **RevoShop** menggunakan PostgreSQL.

Tabel utama yang digunakan:

* `users`
* `orders`
* `order_items`
* `products`
* `categories`

---

## 📂 Struktur File

```text
.
├── schema.sql
├── seed.sql
├── queries.sql
├── ERD_revoshop.png
├── README.md
└── .gitignore
```

Keterangan:

| File               | Deskripsi                                       |
| ------------------ | ----------------------------------------------- |
| `schema.sql`       | Definisi struktur dan tabel database            |
| `seed.sql`         | Data awal/sample data                           |
| `queries.sql`      | Contoh query untuk mengambil dan memfilter data |
| `ERD_revoshop.png` | Diagram relasi antar tabel                      |
| `README.md`        | Dokumentasi project                             |
| `.gitignore`       | File dan folder yang diabaikan oleh Git         |

---

# 🛠️ Persiapan & Setup

## 1. Install PostgreSQL di macOS via Homebrew

### Cek instalasi Homebrew

Buka Terminal dan jalankan:

```bash
brew --version
```

Jika Homebrew belum terinstall, install terlebih dahulu melalui website resmi Homebrew.

### Install PostgreSQL

Jalankan:

```bash
brew install postgresql
```

### Aktifkan layanan PostgreSQL

Setelah instalasi selesai, jalankan:

```bash
brew services start postgresql
```

---

## 2. Verifikasi Instalasi PostgreSQL

### Cek versi PostgreSQL

Jalankan:

```bash
psql --version
```

Contoh output:

```text
psql (PostgreSQL 17.x)
```

### Masuk ke PostgreSQL

Jalankan:

```bash
psql
```

Jika berhasil, prompt PostgreSQL akan terlihat seperti:

```text
username=#
```

Contoh:

```text
heraklosadiafora=#
```

> **Note:** Nama `username` bergantung pada konfigurasi PostgreSQL dan username macOS. Bisa berupa `postgres` atau username macOS yang digunakan saat instalasi.

### Verifikasi user yang sedang digunakan

Di dalam PostgreSQL, jalankan:

```sql
SELECT current_user;
```

### Cek roles PostgreSQL

Jalankan:

```sql
\du
```

Perintah ini akan menampilkan daftar role/user yang tersedia di PostgreSQL.

---

# 🐬 3. Install DBeaver

DBeaver digunakan sebagai GUI untuk mengelola database PostgreSQL.

### Membuat koneksi PostgreSQL

Setelah DBeaver terinstall:

1. Buka **DBeaver**.
2. Pilih **New Database Connection**.
3. Pilih **PostgreSQL**.
4. Isi konfigurasi koneksi:

| Parameter | Value                                    |
| --------- | ---------------------------------------- |
| Host      | `localhost`                              |
| Port      | `5432`                                   |
| Database  | `postgres`                               |
| Username  | Sesuai role PostgreSQL                   |
| Password  | Isi jika PostgreSQL menggunakan password |

5. Klik **Test Connection**.
6. Jika koneksi berhasil, klik **Finish**.

Database PostgreSQL akan muncul di **Database Navigator**.

---

# 🗄️ 4. Membuat Database `revoshop_db`

Setelah berhasil terhubung ke PostgreSQL:

1. Klik kanan pada koneksi PostgreSQL.
2. Pilih **Create → Database**.
3. Masukkan nama database:

```text
revoshop_db
```

4. Klik **Create**.
5. Refresh koneksi PostgreSQL.

Struktur database akan terlihat seperti:

```text
PostgreSQL
└── localhost
    ├── postgres
    └── revoshop_db
```

---

# ▶️ Menjalankan File SQL di DBeaver

Setelah database `revoshop_db` berhasil dibuat, jalankan file SQL secara berurutan:

```text
schema.sql
    ↓
seed.sql
    ↓
queries.sql
```

---

## A. Menjalankan `schema.sql`

File `schema.sql` digunakan untuk membuat struktur database dan tabel.

Langkah-langkah:

1. Buka database `revoshop_db`.
2. Klik kanan database → **SQL Editor → New SQL Script**.
3. Copy isi file `schema.sql`.
4. Paste ke SQL Editor.
5. Jalankan script.
6. Refresh database.

Pastikan tabel berikut sudah muncul:

```text
categories
users
products
orders
order_items
```

---

## B. Menjalankan `seed.sql`

File `seed.sql` digunakan untuk memasukkan sample data ke dalam database.

Langkah-langkah:

1. Buka SQL Editor pada database `revoshop_db`.
2. Copy isi file `seed.sql`.
3. Paste ke SQL Editor.
4. Jalankan script.
5. Pastikan tidak ada error.
6. Refresh bagian **Tables**.

Setelah itu, buka masing-masing tabel untuk memastikan sample data sudah masuk.

---

## C. Menjalankan `queries.sql`

File `queries.sql` berisi contoh query untuk mengambil, mencari, dan memfilter data dari database.

Langkah-langkah:

1. Buka SQL Editor pada database `revoshop_db`.
2. Copy query dari file `queries.sql`.
3. Paste ke SQL Editor.
4. Jalankan query.
5. Periksa hasil query pada tab **Results**.

---

# 🔄 Alur Project

```text
PostgreSQL
    ↓
DBeaver
    ↓
Create database: revoshop_db
    ↓
schema.sql
    ↓
Membuat 5 tabel
    ↓
seed.sql
    ↓
Mengisi sample data
    ↓
queries.sql
    ↓
Mengambil / memfilter data
    ↓
Verifikasi hasil
```

---

# 🗂️ Struktur Database

Database `revoshop_db` terdiri dari 5 tabel utama:

```text
categories
    │
    └── products
            │
            └── order_items
                    │
users ───────── orders
```

Relasi utama:

* Satu `category` dapat memiliki banyak `products`.
* Satu `product` dapat muncul di banyak `order_items`.
* Satu `user` dapat memiliki banyak `orders`.
* Satu `order` dapat memiliki banyak `order_items`.
* `order_items` menghubungkan `orders` dengan `products`.

Untuk melihat gambaran relasi database secara visual, gunakan file:

```text
ERD_revoshop.png
```

---

# ✅ Verifikasi Project

Setelah semua file SQL dijalankan, pastikan:

* [ ] Database `revoshop_db` berhasil dibuat.
* [ ] PostgreSQL dapat terhubung melalui DBeaver.
* [ ] Lima tabel berhasil dibuat.
* [ ] Sample data berhasil dimasukkan.
* [ ] Query pada `queries.sql` dapat dijalankan tanpa error.
* [ ] Hasil query muncul pada tab **Results**.
* [ ] ERD sesuai dengan struktur tabel database.

---

# 📌 Urutan Setup Singkat

Jika PostgreSQL dan DBeaver sudah terinstall, urutan pengerjaan project adalah:

```text
1. Buat database revoshop_db
        ↓
2. Jalankan schema.sql
        ↓
3. Jalankan seed.sql
        ↓
4. Jalankan queries.sql
        ↓
5. Verifikasi tabel dan data
        ↓
6. Cocokkan dengan ERD_revoshop.png
```

---

# 🎯 Tujuan Project

Project ini dibuat untuk memahami dasar-dasar:

* Database relational
* PostgreSQL
* SQL
* Primary Key dan Foreign Key
* Relasi antar tabel
* `INSERT`, `SELECT`, `UPDATE`, dan `DELETE`
* Filtering dan pencarian data
* `JOIN`
* Pengelolaan database menggunakan DBeaver
* Pembuatan dan penggunaan ERD
