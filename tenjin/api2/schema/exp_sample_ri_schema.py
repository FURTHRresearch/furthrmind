from marshmallow import Schema, fields, INCLUDE
from .inner_schema_collection import InnerSchemaWithShortID, InnerSchemaWithoutShortID
from .fielddata_schema import FieldDataSchema, FieldDataPostSchema
from .inner_schema_collection import InnerPostSchema
from .datatable_schema import DataTablePostSchema, DataTableSchema


class ColumnSchema(Schema):
    _id = fields.String(
        data_key="id", required=True, metadata={"description": "The column identifier"}
    )
    Name = fields.String(
        data_key="name", required=True, metadata={"description": "The column name"}
    )


class ExpSampleRiSchema(Schema):
    id = fields.String(metadata={"description": "The identifier"})
    name = fields.String(metadata={"description": "name"})
    shortid = fields.String(metadata={"description": "The short identifier"})
    linked_samples = fields.List(
        fields.Nested(InnerSchemaWithShortID()),
        metadata={"description": "All samples linked to this item"},
    )
    linked_experiments = fields.List(
        fields.Nested(InnerSchemaWithShortID()),
        metadata={"description": "All experiments linked to this"},
    )
    linked_researchitems = fields.Dict(
        keys=fields.String(),
        values=fields.List(fields.Nested(InnerSchemaWithShortID())),
        metadata={"description": "All researchitems belonging to the group"},
    )
    groups = fields.List(
        fields.Nested(InnerSchemaWithoutShortID()),
        metadata={"description": "All sub groups belonging to the group"},
    )
    fielddata = fields.List(
        fields.Nested(FieldDataSchema()),
        metadata={"description": "All field data belonging to the group"},
    )
    files = fields.List(
        fields.Nested(InnerSchemaWithoutShortID()),
        metadata={"description": "All files belonging to the group"},
    )
    protected = fields.Boolean(metadata={"description": "Is the item protected"})
    neglect = fields.Boolean(metadata={"description": "Is the item neglected"})
    datatables = fields.List(
        fields.Nested(DataTableSchema()),
        metadata={"description": "All datatables belonging to the item"},
    )
    category = fields.Nested(
        InnerSchemaWithoutShortID(),
        metadata={"description": "Category of the researchitem, only needed for researchitems"},
    )


class ExpSampleRiPostSchema(Schema):

    _id = fields.String(data_key="id", metadata={"description": "Group ID"})
    ShortID = fields.String(data_key="short_id", metadata={"description": "Short ID"})
    Name = fields.String(data_key="name", metadata={"description": "Group name"})
    Neglect = fields.Boolean(
        data_key="neglect", metadata={"description": "Whether the item is neglected"}
    )
    Protected = fields.Boolean(
        data_key="protected", metadata={"description": "Whether the item is protected"}
    )
    files = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "List of file IDs"},
    )
    fielddata = fields.List(
        fields.Nested(FieldDataPostSchema()),
        metadata={"description": "List of field data, can be any type"},
    )
    groups = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "Parent group IDs"},
    )
    category = fields.Nested(
        InnerPostSchema(),
        metadata={"description": "Category of the experiment/sample/researchitem"},
    )
    datatables = fields.List(
        fields.Nested(DataTablePostSchema()),
        metadata={"description": "List of datatables"},
    )
    rawdata = fields.List(
        fields.Nested(DataTablePostSchema()),
        metadata={"description": "List of datatables"},
    )
    experiments = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "List of experiments to be linked"},
    )
    samples = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "List of samples to be linked"},
    )
    researchitems = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "List of researchitems to be linked"},
    )
