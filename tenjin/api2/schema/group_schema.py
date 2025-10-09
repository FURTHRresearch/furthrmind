from marshmallow import Schema, fields, INCLUDE
from tenjin.api2.schema.inner_schema_collection import (
    InnerSchemaWithShortID,
    InnerSchemaWithoutShortID,
    InnerPostSchema,
)
from tenjin.api2.schema.fielddata_schema import FieldDataSchema
from tenjin.api2.schema.fielddata_schema import FieldDataPostSchema


class GroupSchema(Schema):
    id = fields.String(required=True, metadata={"description": "The group identifier"})
    name = fields.String(required=True, metadata={"description": "Group name"})
    shortid = fields.String(
        required=True, metadata={"description": "The group short identifier"}
    )
    samples = fields.List(
        fields.Nested(InnerSchemaWithShortID()),
        required=True,
        metadata={"description": "All samples belonging to the group"},
    )
    experiments = fields.List(
        fields.Nested(InnerSchemaWithShortID()),
        required=True,
        metadata={"description": "All experiments belonging to the group"},
    )
    sub_groups = fields.List(
        fields.Nested(InnerSchemaWithoutShortID()),
        required=True,
        metadata={"description": "All sub groups belonging to the group"},
    )
    parent_group = fields.Nested(
        InnerSchemaWithoutShortID(),
        required=True,
        metadata={"description": "The parent group of the project"},
    )
    researchitems = fields.Dict(
        required=True,
        keys=fields.String(),
        values=fields.List(fields.Nested(InnerSchemaWithShortID())),
        metadata={"description": "All researchitems belonging to the group"},
    )
    fielddata = fields.List(
        fields.Nested(FieldDataSchema()),
        required=True,
        metadata={"description": "All field data belonging to the group"},
    )
    files = fields.List(
        fields.Nested(InnerSchemaWithoutShortID()),
        required=True,
        metadata={"description": "All files belonging to the group"},
    )


class GroupPostSchema(Schema):

    _id = fields.String(data_key="id", metadata={"description": "Group ID"})
    ShortID = fields.String(data_key="short_id", metadata={"description": "Short ID"})
    Name = fields.String(data_key="name", metadata={"description": "Group name"})
    files = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "List of file IDs"},
    )
    fielddata = fields.List(
        fields.Nested(FieldDataPostSchema()),
        metadata={"description": "List of field data, can be any type"},
    )
    GroupID = fields.String(
        data_key="parent_group", metadata={"description": "Parent group ID"}
    )
