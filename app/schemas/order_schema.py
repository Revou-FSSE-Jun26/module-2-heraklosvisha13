from marshmallow import Schema, fields, validate, post_load

class OrderItemSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

class OrderCreateSchema(Schema):
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))

class OrderUpdateSchema(Schema):
        # Hanya menerima field 'status', dan nilainya harus salah satu dari daftar ini!
    status = fields.Str(
        required=True,
        validate=validate.OneOf(['pending', 'processing', 'shipped', 'completed', 'cancelled'])
    )