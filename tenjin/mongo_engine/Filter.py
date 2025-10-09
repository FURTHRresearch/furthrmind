from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID

class Filter(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "ProjectID"
            ]}



    Name = StringField(required=True)
    NameLower = StringField(required=True, unique_with=["ProjectID"])
    DisplayedColumns = ListField(StringField(), default=list)
    DisplayedCategories = ListField(StringField(), default=list)
    FilterList = ListField(default=list)
    NameFilter = StringField(null=True)
    IncludeLinked = StringField(default="none")


