from marshmallow import Schema, fields, INCLUDE
from .inner_schema_collection import InnerSchemaWithoutShortID

class FieldSchema(Schema):
    _id = fields.String(data_key="id", metadata={"description":"The field identifier"})
    Name = fields.String(data_key="name", metadata={"description":"The field name"})
    Type = fields.String(data_key="type", metadata={"description":"The field type"})
    comboboxentries = fields.List(fields.Nested(InnerSchemaWithoutShortID()), metadata={"description":"The field combobox entries"})
    RawDataCalcScriptFileID = fields.String(data_key="sciptid", metadata={"description":"The field script identifier"})
    WebDataCalcScript = fields.String(data_key="script", metadata={"description":"The field script"})

class FieldPostSchema(Schema):
    _id = fields.String(data_key="id", metadata={"description":"The field identifier"})
    Name = fields.String(data_key="name", metadata={"description":"The field name"})
    Type = fields.String(data_key="type", metadata={"description":"The field type"})