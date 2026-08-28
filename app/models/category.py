# models/category.py
from . import db

class Category(db.Model):
    __tablename__   = 'categories'

    id              = db.Column(db.Integer, primary_key=True)
    category_name   = db.Column(db.String(255), nullable=False, unique=True)

    products        = db.relationship('Product', backref='category', lazy=True)

    def to_dict(self, include_products=False):
        data = {"id": self.id, "category_name": self.category_name}
        if include_products:
            data["products"] = [p.to_dict() for p in self.products]
        return data