from marshmallow import Schema, fields
import json

class IdInputSchema(Schema):
    """
    Schema for validating ID input.
    """
    id = fields.String(required=True, metadata={"description": "The identifier"})
    
class QueryInputSchema(Schema):
    """
    Schema for validating query input.
    """
    def deserialize_fielddata(value):
        ind = value.index(':')
        if ind == -1:
            raise ValueError("Invalid fielddata format, missing ':'")
        fieldname = value[:ind]
        value = value[ind+1:]
        return {"fieldname": fieldname, "value": value}

    id_list = fields.List(fields.String(), data_key='id', required=False, metadata={"description": "List of IDs"})
    short_id_list = fields.List(fields.String(), data_key='shortid', required=False, metadata={"description": "List of short IDs"})
    name_list = fields.List(fields.String(), data_key='name', required=False, metadata={"description": "List of names"})
    category_name = fields.String(data_key='category_name', required=False, metadata={"description": "Category name"})
    category_id = fields.String(data_key='category_id', required=False, metadata={"description": "Category ID"})
    parent_group_id = fields.String(data_key='parent_group_id', required=False, metadata={"description": "Parent group ID"})
    fielddata = fields.List(
        fields.Function(deserialize=deserialize_fielddata),
        data_key="fielddata",
        required=False,
        metadata={"description": "Field data in JSON format"},
    )
    include_linked = fields.Integer(
        data_key="include_linked",
        required=False,
        metadata={"description": "Include linked groups"},
    )
