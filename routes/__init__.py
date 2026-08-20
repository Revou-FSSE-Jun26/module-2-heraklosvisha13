# Import semua routes/blueprint di sini agar bisa diakses dari luar
from .auth_routes import auth_bp, users_bp
from .product_routes import products_bp
from .category_routes import categories_bp
from .order_routes import orders_bp