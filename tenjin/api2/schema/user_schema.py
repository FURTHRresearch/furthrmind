from marshmallow import Schema, fields
from .inner_schema_collection import InnerSchemaWithoutShortID

from .permission_schema import PermissionSchema
    

class UserSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description": "The user identifier"})
    Email = fields.Email(data_key="email", required=True, metadata={"description": "The user's email address"})
    FirstName = fields.String(data_key="firstname", metadata={"description": "The user's first name"})
    LastName = fields.String(data_key="lastname", metadata={"description": "The user's last name"})
    usergroups = fields.List(fields.Nested(InnerSchemaWithoutShortID()), metadata={"description": "The user groups the user belongs to"})
    permissions = fields.List(fields.Nested(PermissionSchema()), metadata={"description": "The permissions the user has"})


class UserPostSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description": "The user identifier"})
    Email = fields.Email(data_key="email", required=True, metadata={"description": "The user's email address"})
    FirstName = fields.String(data_key="firstname", metadata={"description": "The user's first name"})
    LastName = fields.String(data_key="lastname", metadata={"description": "The user's last name"})
    Password = fields.String(data_key="password", required=True, metadata={"description": "The user's password"})
    permissions = fields.List(fields.Nested(PermissionSchema()), metadata={"description": "The permissions the user has"})
    usergroups = fields.List(fields.Nested(InnerSchemaWithoutShortID()), metadata={"description": "The user groups the user belongs to"})
