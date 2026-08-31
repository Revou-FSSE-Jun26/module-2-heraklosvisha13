from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Product, Category, order_items, Order

class ProductService:

    @staticmethod
    def create_product(data):
        # Cek category (jika dikirim)
        if data.get('category_id'):
            category = Category.query.get(data['category_id'])
            if not category:
                raise ValueError("Category not found")

        product = Product(
            name=data['name'],
            price=data['price'],
            stock=data['stock'],
            category_id=data.get('category_id')
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def get_all_products():
        return Product.query.all()

    @staticmethod
    def get_product_by_id(product_id):
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")
        return product

    @staticmethod
    def update_product(product_id, data):
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")

        if 'name' in data:
            product.name = data['name']
        if 'price' in data:
            product.price = data['price']
        if 'stock' in data:
            product.stock = data['stock']
        if 'category_id' in data:
            if data['category_id']:
                category = Category.query.get(data['category_id'])
                if not category:
                    raise ValueError("Category not found")
            product.category_id = data['category_id']

        db.session.commit()
        return product

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")

        # exists = db.session.query(order_items).filter(order_items.c.product_id == product_id).first()
        # baris 66: Hanya check apakah produk ada di order_items atau tidak sehingga jika ada tidak dapat dihapus
        
        active = ("pending", "processing", "shipped")

        exists = (db.session.query(order_items) #ambil data dari table order_items
                .join(Order, Order.id == order_items.c.order_id) #gabung data order_items dan order dengan syarat order.id == order_items.order_id
                .filter(order_items.c.product_id == product_id, Order.status.in_(active)) #lakukan filtering untuk mengambil 2 kondisi AND
                .first())
        # baris 69: Check apakah produk

        if exists:
            raise PermissionError("Cannot delete product: active orders exist")

        db.session.delete(product)
        db.session.commit()
        return True