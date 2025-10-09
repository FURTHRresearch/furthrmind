from marshmallow import Schema, fields, INCLUDE
from .inner_schema_collection import InnerUnitSchema
from .unit_schema import UnitPostSchema


class ColumnSchema(Schema):
    _id = fields.String(
        data_key="id", required=True, metadata={"description": "The column identifier"}
    )
    Name = fields.String(
        data_key="name", required=True, metadata={"description": "The column name"}
    )
    Type = fields.String(
        data_key="type", required=True, metadata={"description": "The column type"}
    )
    unit = fields.Nested(
        InnerUnitSchema(), metadata={"description": "The unit identifier"}
    )
    Data = fields.List(
        fields.Raw(), data_key="values", metadata={"description": "The column values"}
    )


class ColumnPostSchema(Schema):

    def deserialize_unit(value):
        try:
            value = UnitPostSchema().load(value)
        except:
            value = None
        return value

    Name = fields.String(
        data_key="name", required=True, metadata={"description": "The column name"}
    )
    Type = fields.String(
        data_key="type", required=True, metadata={"description": "The column type"}
    )
    unit = fields.Function(
        deserialize=deserialize_unit,
        metadata={"description": "The unit identifier"},
        allow_none=True,
    )
    values = fields.List(fields.Raw(), metadata={"description": "The column values"})
