from marshmallow import Schema, fields

    
class GetAllStandardSchema(Schema):
    """
    Schema for getting all standard data.
    """
    id = fields.String(required=True, metadata={"description": "The standard identifier"})
    Name = fields.String(data_key="name", required=True, metadata={"description": "The standard name"})
    ShortID = fields.String(data_key="shortid", required=True, metadata={"description": "The standard short identifier"})
    