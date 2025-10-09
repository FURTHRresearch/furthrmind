from marshmallow import Schema, fields, INCLUDE
from tenjin.api2.schema.inner_schema_collection import (InnerSchemaWithShortID, InnerSchemaWithoutShortID,
                                                        InnerUnitSchema, InnerFieldSchema)


class UserSchema(Schema):
    id = fields.String(required=True, metadata={"description":"The user identifier"})
    email = fields.String(required=True, metadata={"description":"The user's email address"})
    read = fields.Boolean(required=True, metadata={"description":"Has read access"})
    write = fields.Boolean(required=True, metadata={"description":"Has write access"})
    delete = fields.Boolean(required=True, metadata={"description":"Has delete access"})
    admin = fields.Boolean(required=True, metadata={"description":"Has admin rights"})
    owner = fields.Boolean(required=True, metadata={"description":"User is project owner"})

class UserGroupSchema(Schema):
    name = fields.String(required=True, metadata={"description":"The name of the user group"})
    read = fields.Boolean(required=True, metadata={"description":"Has read access"})
    write = fields.Boolean(required=True, metadata={"description":"Has write access"})
    delete = fields.Boolean(required=True, metadata={"description":"Has delete access"})
    admin = fields.Boolean( required=True, metadata={"description":"Has admin access"})


class OwnerSchema(Schema):
    id = fields.String(required=True, metadata={"description":"The user identifier"})
    email = fields.String(required=True, metadata={"description":"The user's email address"})
    
    
class PermissionSchema(Schema):
    owner = fields.Nested(OwnerSchema(), metadata={"description":"The owner of the project"})
    users = fields.List(fields.Nested(UserSchema()), metadata={"description":"User with permission to the project"})
    usergroups = fields.List(fields.Nested(UserGroupSchema()), metadata={"description":"User groups with permission to the"})

class ProjectSchema(Schema):
    _id = fields.String(data_key="id", required=True, metadata={"description":"The project identifier"})
    Name = fields.String(data_key="name", required=True, metadata={"description":"Project name"})
    Info = fields.String(data_key="info", required=True, metadata={"description":"Project information"})
    ShortID = fields.String(data_key="shortID", required=True, metadata={"description":"The project short identifier"})
    samples = fields.List(fields.Nested(InnerSchemaWithShortID()), required=True, metadata={"description":"All groups belonging to the project"})
    experiments = fields.List(fields.Nested(InnerSchemaWithShortID()), required=True, metadata={"description":"All groups belonging to the project"})
    groups = fields.List(fields.Nested(InnerSchemaWithShortID()), required=True, metadata={"description":"All groups belonging to the project"})
    units = fields.List(fields.Nested(InnerUnitSchema()), required=True, metadata={"description":"All units belonging to the project"})
    researchitems = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(InnerSchemaWithShortID())))
    permissions = fields.Nested(PermissionSchema(), required=True, metadata={"description":"All permissions belonging to the project"})
    fields = fields.List(fields.Nested(InnerFieldSchema()), required=True, metadata={"description":"All field belonging to the project"})

class ProjectPostSchema(Schema):
    Name = fields.String(data_key="name", metadata={"description":"Project name"})
    Info = fields.String(data_key="info", metadata={"description":"Project information"})
    _id = fields.String(data_key="id", metadata={"description":"Project ID"})

class ProjectAllSchema(Schema):
    id = fields.String(metadata={"description":"Project identifier"})
    name = fields.String( metadata={"description":"Project name"})
    info = fields.String( metadata={"description":"Project information"})
    
