from marshmallow import Schema, fields, INCLUDE
from .exp_sample_ri_schema import ExpSampleRiSchema

class ResearchCategorySchema(Schema):
    _id = fields.String(data_key="id", metadata={"description": "The research category identifier"})
    Name = fields.String(data_key="name", metadata={"description": "The research category name"})

class ResearchItemSchema(ExpSampleRiSchema):
    category = fields.Nested(ResearchCategorySchema(), metadata={"description": "The category of the research item"})