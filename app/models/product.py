# models/product.py
from . import db

class Product(db.Model):
    __tablename__   = 'products'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(255), nullable=False)
    price           = db.Column(db.Numeric(15, 2), nullable=False)
    stock           = db.Column(db.Integer, nullable=False, default=0)
    category_id     = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "stock": self.stock,
            "category_id": self.category_id
        }