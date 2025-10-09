from marshmallow import Schema, fields, INCLUDE
from .inner_schema_collection import InnerSchemaWithoutShortID, InnerPostSchema


class DataTableSchema(Schema):
    _id = fields.String(
        data_key="id",
        required=True,
        metadata={"description": "The data table identifier"},
    )
    Name = fields.String(
        data_key="name", required=True, metadata={"description": "The data table name"}
    )
    columns = fields.List(
        fields.Nested(InnerSchemaWithoutShortID()),
        metadata={"description": "The columns of the data table"},
    )


class DataTablePostSchema(Schema):
    _id = fields.String(
        data_key="id",
        metadata={"description": "The data table identifier"},
    )
    Name = fields.String(
        data_key="name", metadata={"description": "The data table name"}
    )
    columns = fields.List(
        fields.Nested(InnerPostSchema()),
        metadata={"description": "The columns of the data table"},
        required=False
    )

    exp = fields.Nested(
        InnerPostSchema(),
        data_key="experiment",
        metadata={"description": "The exp_id the datatable should belong to"},
    )
    
    sample = fields.Nested(
        InnerPostSchema(),
        metadata={"description": "The sample ID the datatable should belong to"},
    )
    
    researchitem = fields.Nested(
        InnerPostSchema(),
        metadata={"description": "The research_item ID the datatable should belong to"},
    )
