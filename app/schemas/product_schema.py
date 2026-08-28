from marshmallow import Schema, fields, validate

class ProductCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Int(required=True, validate=validate.Range(min=0))
    category_id = fields.Int(allow_none=True)

class ProductUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1))
    price = fields.Float(validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0))
    category_id = fields.Int(allow_none=True)