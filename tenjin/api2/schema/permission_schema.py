from marshmallow import Schema, fields
from .inner_schema_collection import InnerSchemaWithoutShortID



class PermissionSchema(Schema):
    project = fields.Nested(InnerSchemaWithoutShortID(), required=True, metadata={"description": "The project"})
    read = fields.Boolean(required=True, metadata={"description": "Has read access"})
    write = fields.Boolean(required=True, metadata={"description": "Has write access"})
    delete = fields.Boolean(required=True, metadata={"description": "Has delete access"})
    admin = fields.Boolean(required=True, metadata={"description": "Has admin rights"})
    owner = fields.Boolean(required=True, metadata={"description": "User is project owner"})
    