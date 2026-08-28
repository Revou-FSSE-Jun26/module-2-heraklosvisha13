from marshmallow import Schema, fields, validate

class CategoryCreateSchema(Schema):
    category_name = fields.Str(required=True, validate=validate.Length(min=1))

class CategoryUpdateSchema(Schema):
    category_name = fields.Str(required=True, validate=validate.Length(min=1))