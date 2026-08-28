from marshmallow import Schema, fields, validate, post_load

class OrderItemSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

class OrderCreateSchema(Schema):
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))