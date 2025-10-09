from marshmallow import Schema, fields, INCLUDE
from .inner_schema_collection import InnerSchemaWithoutShortID

class FilePostSchema(Schema):
    _id = fields.String(data_key="id", metadata={"description":"The field identifier"})
    Name = fields.String(data_key="name", metadata={"description":"The field name"})
    S3Key = fields.String(data_key="s3key", metadata={"description":"The field type"})