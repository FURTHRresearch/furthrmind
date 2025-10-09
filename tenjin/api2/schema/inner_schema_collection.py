from marshmallow import Schema, fields
from bson import ObjectId

class InnerSchemaWithShortID(Schema):
    _id = fields.String(data_key="id", metadata={"description":"The identifier"})
    Name = fields.String(data_key="name", metadata={"description":"The name"})
    ShortID = fields.String(data_key="shortID", metadata={"description":"The short identifier"})

class InnerSchemaWithoutShortID(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description":"The identifier"})
    Name = fields.String(data_key="name", required=True, metadata={"description":"The name"})


class InnerUnitSchema(Schema):
    _id = fields.String(data_key="id", metadata={"description":"The unit identifier"})
    ShortName = fields.String(data_key="name", metadata={"description":"Unit short name"})
    LongName = fields.String(data_key="longname", metadata={"description":"Unit long name"})


class InnerFieldSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description":"The field identifier"})
    Name = fields.String(data_key="name",required=True, metadata={"description":"The field name"})
    Type = fields.String(data_key="type",required=True, metadata={"description":"The field type"})
    comboboxentries = fields.List(fields.Nested(InnerSchemaWithoutShortID()), metadata={"description":"The field combobox entries"})    


class InnerPostSchema(Schema):
    def convert_to_object_id(value):
        try:
            value = ObjectId(value)
            return value
        except:
            raise ValueError(f"Value {value} is not a valid ObjectId")
        

    _id = fields.Function(data_key="id", deserialize=convert_to_object_id, metadata={"description":"The identifier"})
    Name = fields.String(data_key="name", metadata={"description":"The name"})

