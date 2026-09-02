# models/order.py
from datetime import datetime
from . import db

# Tabel Asosiasi Many-to-Many
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('unit_price', db.Numeric(15, 2), nullable=False)
)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', secondary=order_items, backref=db.backref('orders', lazy='dynamic'))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_price": float(self.total_price),
            "status": self.status,
            "created_at": self.created_at
        }