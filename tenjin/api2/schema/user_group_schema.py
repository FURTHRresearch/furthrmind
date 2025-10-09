from marshmallow import Schema, fields
from .inner_schema_collection import InnerSchemaWithoutShortID
from .user_schema import UserSchema, PermissionSchema


class UserGroupSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description": "The user identifier"})
    Name = fields.String(data_key="name", required=True, metadata={"description": "The user group name"})
    users = fields.List(fields.Nested(UserSchema()), metadata={"description": "The users in the group"})
    permissions = fields.List(fields.Nested(PermissionSchema()), metadata={"description": "The permissions the user has"})

class UserGroupPostSchema(Schema):
    _id = fields.String(data_key="id", metadata={"description": "The user identifier"})
    Name = fields.String(data_key="name", required=True, metadata={"description": "The user group name"})
    users = fields.List(fields.Nested(InnerSchemaWithoutShortID()), metadata={"description": "The users in the group"})
    permissions = fields.List(fields.Nested(PermissionSchema()), metadata={"description": "The permissions the user has"})