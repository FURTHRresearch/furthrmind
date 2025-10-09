import flask
from mongoengine import *
from .BaseClass import BaseClass
from datetime import datetime

class Versioning(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                "DataID",
                "ExecutionTime",
                ("DataID", "ExecutionTime"),
            ]}


    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        if flag in ["read", "delete", "invite"]:
            return [], {doc.id: False for doc in document_list}
        else:
            return document_list, {doc.id: True for doc in document_list}

    @staticmethod
    def add_entry(document, kwargs, user_id=None):
        collection = document.__class__.__name__
        attribute = kwargs.get("Attr", None)
        value = kwargs.get("Value", None)
        operation = kwargs.get("Opr", None)
        from tenjin.mongo_engine import Database
        if "NoVersioning" in kwargs:
            if kwargs["NoVersioning"]:
                return
            
        if user_id is None:
            if collection == "User" and operation == "Create":
                user_id = None
            else:
                # if get_from_redis("LayoutCheck") == "1":
                if Database.check_for_no_access_check():
                    user_id = None
                else:
                    try:
                        user_id = flask.g.user
                    except:
                        pass

        if collection == "User":
            if operation == "Create":
                if "Password" in value:
                    value = value.pop("Password")
            elif operation == "Update" and attribute == "Password":
                value = None

        v = Versioning(
            DataID=document.id,
            Collection=collection,
            Attribute=attribute,
            Operation=operation,
            Value=value,
            ExecutingUserID=user_id
        )
        v.save()

    DataID = ObjectIdField(required=True)
    Collection = StringField(required=True)
    Attribute = StringField(null=True)
    Operation = StringField(required=True)
    Value = DynamicField(null=True)
    ExecutionTime = DateTimeField(default=datetime.utcnow)
    ExecutingUserID = LazyReferenceField("User", null=True)

