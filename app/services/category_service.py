from app.models import db, Category

class CategoryService:

    @staticmethod
    def create_category(data):
        existing = Category.query.filter_by(category_name=data['category_name']).first()
        if existing:
            raise ValueError("Category name already exists")

        category = Category(category_name=data['category_name'])
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def get_all_categories():
        return Category.query.all()

    @staticmethod
    def get_category_by_id(category_id):
        category = Category.query.get(category_id)
        if not category:
            raise ValueError("Category not found")
        return category

    @staticmethod
    def update_category(category_id, data):
        category = Category.query.get(category_id)
        if not category:
            raise ValueError("Category not found")

        # Cek duplikat nama (kecuali dirinya sendiri)
        existing = Category.query.filter(
            Category.id != category_id,
            Category.category_name == data['category_name']
        ).first()
        if existing:
            raise ValueError("Category name already exists for another category")

        category.category_name = data['category_name']
        db.session.commit()
        return category

    @staticmethod
    def delete_category(category_id):
        category = Category.query.get(category_id)
        if not category:
            raise ValueError("Category not found")

        # Cek apakah ada produk yang masih menggunakan kategori ini
        if category.products:
            raise PermissionError("Cannot delete category: products still exist in this category")

        db.session.delete(category)
        db.session.commit()
        return True