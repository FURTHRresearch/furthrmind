from marshmallow import Schema, fields, INCLUDE

class ResearchCategorySchema(Schema):
    id = fields.String(required=True, metadata={"description": "The research category identifier"})
    Name = fields.String(data_key="name", required=True, metadata={"description": "The research category name"})
    Description = fields.String(data_key="description", metadata={"description": "The research category description"})
    ProjectID = fields.String(data_key="project_id", required=True, metadata={"description": "The project identifier"})
    

class ResearchCategoryPostSchema(Schema):
    Name = fields.String(data_key="name", required=True, metadata={"description": "The research category name"})
    Description = fields.String(data_key="description", metadata={"description": "The research category description"})
    