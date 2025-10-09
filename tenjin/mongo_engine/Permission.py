from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID
import flask
from bson import ObjectId
from mongoengine.base.datastructures import LazyReference
from tenjin.tasks.rq_task import create_task

class Permission(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "ProjectID",
                ("id", "ProjectID")
            ]}

    GroupNoWriteIDList = ListField(LazyReferenceField("Group"), default=list)   # , reverse_delete_rule=PULL
    GroupNoReadIDList = ListField(LazyReferenceField("Group"), default=list)
    GroupNoDeleteIDList = ListField(LazyReferenceField("Group"), default=list)
    Write = BooleanField(default=False)
    Read = BooleanField(default=False)
    Delete = BooleanField(default=False)
    Invite = BooleanField(default=False)

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        """
        Updates are only allowed by user with invite access to the project
        """
        from tenjin.mongo_engine import Database

        document_list_original = list(document_list)
        first = document_list[0]
        if isinstance(first, LazyReference):
            id_list = [d.id for d in document_list_original]
            document_list = cls.objects(id__in=id_list).only()
        elif isinstance(first, ObjectId):
            id_list = document_list
            document_list = cls.objects(id__in=id_list).only()
        elif isinstance(first, dict):
            document_id_list = [d["_id"] for d in document_list]
            document_list = cls.objects(id__in=document_id_list).only()

        if flag == "read":
            return document_list, {doc.id: True for doc in document_list}

        if Database.check_for_no_access_check():
            return document_list, {doc.id: True for doc in document_list}

        # get user
        from .User import User
        if user is None:
            user = flask.g.user
        if isinstance(user, LazyReference):
            user = user.fetch()
        elif isinstance(user, ObjectId):
            user = User.objects(id=user)[0]

        if user["Admin"]:
            return document_list, {doc.id: True for doc in document_list}

        result_list, result_dict = super().check_permission(document_list, "invite", user, signal_kwargs)
        return result_list, result_dict

    @classmethod
    def post_save_method(cls, sender, document, **kwargs):
        from tenjin.execution.update import Update
        super().post_save_method(sender, document, **kwargs)

        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if attr == "Invite" and value is True:
            Update.update("Permission", "Read", True, document.id)
            Update.update("Permission", "Write", True, document.id)
            Update.update("Permission", "Delete", True, document.id)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)

        from .User import User
        from .UserGroup import UserGroup

        collection_attribute_list = [
            {"class": User,
             "attr": User.PermissionIDList.name},
            {"class": UserGroup,
             "attr": UserGroup.PermissionIDList.name}
        ]
        Permission.post_delete_pull(collection_attribute_list, document.id)

    def update_method(self, kwargs):
        from tenjin.mongo_engine.User import User
        from tenjin.web.helper.email_helper import send_email

        if not kwargs:
            return

        if kwargs.get("Attr") in ["Write", "Read", "Delete", "Invite"]:
            user = User.objects(PermissionIDList__in=[self.id]).first()
            if not user:
                "Permission belongs to user group. No email will be send"
                return
            project = self.ProjectID.fetch()
            access_string = f"Read: {self.Read}, Write: {self.Write}, Delete: {self.Delete}, Project administration: {self.Invite}"

            root_url = flask.current_app.config.get("ROOT_URL")
            link = f"{root_url}/projects/{project.id}/data"
            if access_string:

                body = flask.render_template('emails/project_rights_changed.html',
                                             project=project.Name,
                                             access=access_string,
                                             link=link)

                if kwargs.get("send_email"):
                    create_task(send_email, user.Email, 'FURTHRmind: Project Access Rights Changed', body)

    
