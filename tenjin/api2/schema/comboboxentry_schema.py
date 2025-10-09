from marshmallow import Schema, fields, INCLUDE
from .inner_schema_collection import InnerSchemaWithoutShortID, InnerPostSchema
from .fielddata_schema import FieldDataSchema, FieldDataPostSchema


class ComboBoxEntrySchema(Schema):
    _id = fields.String(
        data_key="id",
        required=True,
        metadata={"description": "The combobox entry identifier"},
    )
    Name = fields.String(
        data_key="name",
        required=True,
        metadata={"description": "The combobox entry name"},
    )
    field = fields.Nested(
        InnerSchemaWithoutShortID(), metadata={"description": "The associated field"}
    )
    files = fields.List(
        fields.Nested(InnerSchemaWithoutShortID()),
        metadata={"description": "The combobox entry files"},
    )
    fielddata = fields.List(
        fields.Nested(FieldDataSchema()),
        metadata={"description": "The combobox entry field data"},
    )


class ComboBoxEntryPostSchema(Schema):

    _id = fields.String(
        data_key="id", metadata={"description": "The combobox entry identifier"}
    )
    Name = fields.String(
        data_key="name", metadata={"description": "The combobox entry name"}
    )
    field = fields.Nested(
        InnerPostSchema(), metadata={"description": "The associated field"}
    )
    files = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "The combobox entry files"},
    )
    fielddata = fields.List(
        fields.Nested(FieldDataPostSchema()),
        metadata={"description": "The combobox entry field data"},
    )
