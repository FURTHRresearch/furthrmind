from mongoengine import *
from .BaseClass import BaseClass
import flask
from bson import ObjectId
from mongoengine.base.datastructures import LazyReference

class UserGroup(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                "UserIDList",
                "PermissionIDList",
                "NameLower"
            ]
            }


    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        """
        only admin can create a user group, but only without permissions
        everybody can read user group information
        only admin can update user group
        only user with invite access to certain project can add certain permission
        """
        from .User import User
        from .Permission import Permission
        from tenjin.mongo_engine import Database

        if isinstance(document_list[0], ObjectId):
            doc_id_list = document_list
        else:
            doc_id_list = [doc.id for doc in document_list]

        if flag == "read":
            return document_list, {doc_id: True for doc_id in doc_id_list}

        if Database.check_for_no_access_check():
        # if get_from_redis("LayoutCheck") == "1":
            return document_list, {doc.id: True for doc in document_list}

        # get user
        if user is None:
            user = flask.g.user
        if isinstance(user, LazyReference):
            user = user.fetch()
        elif isinstance(user, ObjectId):
            user = User.objects(id=user)[0]

        operation = attribute = None
        if signal_kwargs is not None:
            operation = signal_kwargs.get("Opr", None)
            attribute = signal_kwargs.get("Attr", None)

        if operation is None:
            operation = "Create"

        if operation in ["Create", "Delete"]:
            if user["Admin"]:
                return document_list, {doc_id: True for doc_id in doc_id_list}
            else:
                return [], {doc_id: False for doc_id in doc_id_list}

        elif operation in ["Update", "Append"]:
            if user["Admin"]:
                return document_list, {doc_id: True for doc_id in doc_id_list}

            if attribute == "PermissionIDList":
                # check if current user has access to permission, if so he is allowed to append the permission to another user
                permission_id = signal_kwargs.get("Value")
                permission_id_list, permission_result_dict = Permission.check_permission([permission_id], "invite", user)
                return permission_id_list, permission_result_dict

            return [], {doc_id: False for doc_id in doc_id_list}

        elif operation == "Pop":

            if attribute == "PermissionIDList":
                # check if current user has access to permission, if so he is allowed to append the permission to another user
                permission_id = signal_kwargs.get("Value")
                permission = Permission.objects.get(id=permission_id).first()
                if permission is None:
                    # permission already deleted => post remove from user object => allow operation
                    return document_list, {doc_id: True for doc_id in doc_id_list}

                permission_id_list, permission_result_dict = Permission.check_permission([permission_id], "invite",
                                                                                         user)
                return permission_id_list, permission_result_dict

            if user["Admin"]:
                return document_list, {doc_id: True for doc_id in doc_id_list}
            else:
                return [], {doc_id: False for doc_id in doc_id_list}



    Name = StringField(required=True)
    NameLower = StringField(required=True, unique=True)
    UserIDList = ListField(LazyReferenceField("User"), default=list)    # reverse_delete_rule=PULL
    PermissionIDList = ListField(LazyReferenceField("Permission"), default=list)  # reverse_delete_rule=PULL
