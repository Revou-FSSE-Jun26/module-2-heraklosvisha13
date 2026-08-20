# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# 1. Buat objek db di sini (agar semua model pakai db yang sama)
db = SQLAlchemy()

# 2. Import semua model di sini agar bisa diakses dari luar
# (Misal: from models import User, Product)
from .user import User
from .category import Category
from .product import Product
from .order import Order, order_items