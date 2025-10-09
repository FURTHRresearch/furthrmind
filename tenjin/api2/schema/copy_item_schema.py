from marshmallow import Schema, fields

class CopyItemPostSchema(Schema):

    collection = fields.String(required=True, metadata={"description": "The collection name"})
    templateID = fields.String(required=True, metadata={"description": "The template ID"})
    projectID = fields.String(required=True, metadata={"description": "The project ID"})
    groupid = fields.String(required=True, metadata={"description": "The group ID"})
    include_exp = fields.Boolean(default=False, metadata={"description": "Include experiments"})
    include_sample = fields.Boolean(default=False, metadata={"description": "Include samples"})
    include_researchitem = fields.Boolean(default=False, metadata={"description": "Include research items"})
    include_subgroup = fields.Boolean(default=False, metadata={"description": "Include subgroups"})
    include_raw_data = fields.Boolean(default=False, metadata={"description": "Include raw data"})
    include_files = fields.Boolean(default=False, metadata={"description": "Include files"})
    include_fields = fields.Boolean(default=False, metadata={"description": "Include fields"})
    
    