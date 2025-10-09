from marshmallow import Schema, fields, INCLUDE

class UnitSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description": "The unit identifier"})
    ShortName = fields.String(data_key="name", required=True, metadata={"description": "The unit short name"})
    LongName = fields.String(data_key="longname", metadata={"description": "The unit long name"})
    original_definition_string = fields.String(metadata={"description": "The original unit definition"})

class UnitPostSchema(Schema):
    _id = fields.String(data_key="id", metadata={"description": "The unit identifier"})
    ShortName = fields.String(data_key="name", metadata={"description": "The unit short name"})
    definition = fields.String(metadata={"description": "The unit definition"})

