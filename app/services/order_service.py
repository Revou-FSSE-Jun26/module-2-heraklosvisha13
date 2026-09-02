from app.models import db, Order, Product, order_items

class OrderService:

    @staticmethod
    def create_order(user_id, items_data):
        total_price = 0
        order_items_list = []

        for item in items_data:
            print(item['product_id'], item['quantity'])
            product = Product.query.get(item['product_id'])
            if not product:
                raise ValueError(f"Product {item['product_id']} not found")

            if product.stock < item['quantity']:
                raise ValueError(f"Insufficient stock for '{product.name}'")

            product.stock -= item['quantity']
            total_price += product.price * item['quantity']
            order_items_list.append({
                "product_id": product.id,
                "quantity": item['quantity'],
                "unit_price": float(product.price)
            })

        order = Order(user_id=user_id, total_price=total_price, status='pending')
        db.session.add(order)
        db.session.flush()

        for item in order_items_list:
            db.session.execute(order_items.insert().values(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            ))

        db.session.commit()
        return order

    @staticmethod
    def get_orders_by_user(user_id):
        return Order.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_order_by_id(order_id, user_id):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != user_id:
            raise PermissionError("Unauthorized to view this order")
        return order

    @staticmethod
    def delete_order(order_id, user_id):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != user_id:
            raise PermissionError("Unauthorized to delete this order")

        db.session.delete(order)
        db.session.commit()
        return True

    @staticmethod
    def get_order_with_items(order_id, user_id):
        order = OrderService.get_order_by_id(order_id, user_id)

        items = []
        for product in order.products:
            item = db.session.execute(
                order_items.select().where(
                    order_items.c.order_id == order_id,
                    order_items.c.product_id == product.id
                )
            ).first()
            items.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.quantity * item.unit_price)
            })

        return {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": float(order.total_price),
            "status": order.status,
            "created_at": order.created_at,
            "items": items
        }
    @staticmethod
    def update_order(order_id, user_id, data):
        """
        Update status order. Hanya pemilik order yang boleh mengupdate.
        Jika order sudah 'completed', tidak boleh diubah lagi.
        """
        # Cari order
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Otorisasi: Cek apakah order ini milik user yang login
        if order.user_id != user_id:
            raise PermissionError("Unauthorized to update this order")
        
        # Cek apakah order sudah "completed"
        if order.status == "completed":
            raise PermissionError("Cannot update order: already completed")
        # ============================================================
        
        # Ambil status baru dan validasi (Marshmallow sudah mengecek, tapi kita cek lagi)
        new_status = data['status']
        
        # Update status
        order.status = new_status
        db.session.commit()
        
        return order