from mongoengine import *
from .BaseClass import BaseClass


class Trigger(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                "DataID"
            ]
            }

    DataID = ObjectIdField(required=True)#, reverse_delete_rule=CASCADE)
    Attribute = StringField(null=True)
    Collection = StringField(required=True)
    Value = DynamicField(null=True)


