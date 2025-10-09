from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID
import datetime

class DataViewChart(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "DataViewID"
            ]}

    Name = StringField(required=True)
    DataViewID = LazyReferenceField("DataView", required=True)  #, reverse_delete_rule
    XAxis = StringField(null=True)
    YAxis = StringField(null=True)
    Data = ListField(null=True)
    DataUpdated = DateTimeField(null=True)


