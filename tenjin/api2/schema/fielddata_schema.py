from marshmallow import Schema, fields, validates
from tenjin.api2.schema.inner_schema_collection import InnerUnitSchema
from tenjin.api2.schema.unit_schema import UnitPostSchema


class AuthorSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description":"The author identifier"})
    Name = fields.String(data_key="name", metadata={"description":"The author name"})
    Institution = fields.String(data_key="institution", metadata={"description":"The author institution"})
    UserID = fields.String(data_key="user", metadata={"description":"The author user id"})


class FieldDataSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description":"The field identifier"})
    fieldname = fields.String(required=True, metadata={"description":"The field name"})
    Type = fields.String(data_key="fieldtype", required=True, metadata={"description":"The field type"})
    FieldID = fields.String(data_key="fieldid", required=True, metadata={"description":"The field value"})
    si_value = fields.Float(required=True, metadata={"description":"The field value"}, 
                             allow_none=True)
    unit = fields.Nested(InnerUnitSchema(), metadata={"description":"The unit of the field"}, 
                         allow_none=True)
    author = fields.Nested(AuthorSchema(), metadata={"description":"The author of the field"})
    value = fields.Raw(metadata={"description":"The field value"})
    
    
class FieldDataPostSchema(Schema):   
    _id = fields.String(data_key="id", metadata={"description":"The field identifier"})
    field_name = fields.String(data_key="fieldname", metadata={"description":"The field name"})
    field_type = fields.String(data_key="fieldtype", metadata={"description":"The field type"})
    field_id = fields.String(data_key="fieldid", metadata={"description":"The field type"})
    value = fields.Raw(metadata={"description":"The field value"}, allow_none=True)
    unit = fields.Nested(UnitPostSchema(), metadata={"description":"The unit of the field"}, allow_none=True)
