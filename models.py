from datetime import datetime
from utils import db


# Association Table
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('unit_price', db.Numeric(10, 2), nullable=False)
)

class User(db.Model):
    __tablename__   = 'users'

    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(255), nullable=False, unique=True)
    password_hash   = db.Column(db.String(255), nullable=False)
    email           = db.Column(db.String(255), nullable=False, unique=True)
    role            = db.Column(db.String(20), server_default='customer')  # Added role field with default value
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    orders          = db.relationship('Order', backref='user', lazy=True)


class Category(db.Model):
    __tablename__   = 'categories'

    id              = db.Column(db.Integer, primary_key=True)
    category_name   = db.Column(db.String(255), nullable=False, unique=True)

    products        = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    __tablename__   = 'products'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(255), nullable=False)
    price           = db.Column(db.Numeric(10, 2), nullable=False)
    stock           = db.Column(db.Integer, nullable=False, default=0)
    category_id     = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def show_list(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "stock": self.stock,
            "category_id": self.category_id
        }


class Order(db.Model):
    __tablename__   = 'orders'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price     = db.Column(db.Numeric(10, 2), nullable=False)
    status          = db.Column(db.String(50), nullable=False, default='pending')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi Many-to-Many ke Product (melalui order_items)
    products = db.relationship('Product', secondary=order_items, backref=db.backref('orders', lazy='dynamic'))

