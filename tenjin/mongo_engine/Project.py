import bson
import flask
from mongoengine import *
from mongoengine.base.datastructures import LazyReference

from tenjin.tasks.rq_task import create_task
from .BaseClass import BaseClass


class Project(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                "NameLower",
                "ShortID",
            ]
            }

    FileIDList = ListField(LazyReferenceField("File"), default=list)
    Name = StringField(required=True)
    NameLower = StringField(required=True, unique=True)
    Info = StringField(null=True)
    ShortID = StringField(null=True)
    GlobalTemplate = BooleanField(default=False)
    UserTemplate = BooleanField(default=False)
    Archived = BooleanField(default=False)

    @staticmethod
    def get_prefix():
        return "prj"

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            document.generate_short_id()

    def create_method(self, kwargs):
        for attr in [Project.FileIDList]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        from tenjin.web.helper.email_helper import send_email
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == Project.FileIDList.name:
            from .File import File

            File.update_project_external_triggered(self.FileIDList, self.id)

        if attr == Project.OwnerID.name:
            user = self.OwnerID.fetch()
            root_url = flask.current_app.config.get("ROOT_URL")
            link = f"{root_url}/projects/{self.id}/data"
            body = flask.render_template('emails/project_owner.html',
                                         project=self.Name,
                                         link=link)
            create_task(send_email, user.Email, 'FURTHRmind: Project Owner Changed', body)

    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == Project.FileIDList.name:
            from .File import File

            File.update_project_external_triggered([value], self.id)

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        """
        Only delete or update Archive flag only for owner and project admin
        Rest normal permissions
        """
        from tenjin.mongo_engine import Database

        if Database.check_for_no_access_check():
            (
                document_id_list,
                document_list,
                document_mapping_original,
                document_list_original,
            ) = cls.prepare_document_list_for_permission_check(document_list)
            result_dict = {d_id: True for d_id in document_id_list}
            return document_list_original, result_dict

        from .User import User

        # get user
        if user is None:
            user = flask.g.user

        if isinstance(user, LazyReference):
            user = user.fetch()
        elif isinstance(user, User):
            pass
        elif isinstance(user, bson.ObjectId):
            user = User.objects(id=user).first()

        if flag == "delete":
            result_list, result_dict = cls.check_delete_or_archive_permission(document_list, user)
            return result_list, result_dict

        elif flag == "write":
            if signal_kwargs:
                if signal_kwargs.get("Attr") == "Archived":
                    result_list, result_dict = cls.check_delete_or_archive_permission(document_list, user)
                    return result_list, result_dict

        return super().check_permission(document_list, flag, user, signal_kwargs)

    @classmethod
    def check_delete_or_archive_permission(cls, document_list, user):
        from tenjin.mongo_engine.Permission import Permission

        """ user is User object"""
        (
            document_id_list,
            document_list,
            document_mapping_original,
            document_list_original,
        ) = cls.prepare_document_list_for_permission_check(document_list)

        access_id_list = []
        for doc in document_list:
            if doc.OwnerID is None:
                if user.Admin:
                    access_id_list.append(doc.id)
            else:
                if doc.OwnerID.id == user.id:
                    access_id_list.append(doc.id)
                else:
                    p_ids = cls.get_permission_ids_of_user_to_project(doc.id, user.id)
                    permissions = Permission.objects(id__in=p_ids)
                    for p in permissions:
                        if p.Invite:
                            access_id_list.append(doc.id)

        result_list, result_dict = cls.prepare_result_permission_check(
            document_id_list, access_id_list, document_mapping_original
        )
        return result_list, result_dict

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        from tenjin.mongo_engine import Database
        super().post_delete_method(sender, document, **kwargs)

        collection_class_strings = Database.get_all_collection_classes()
        collection_attribute_list = []
        for class_string in collection_class_strings:
            _class = Database.get_collection_class(class_string)
            if hasattr(_class, "ProjectID"):
                collection_attribute_list.append(
                    {
                        "class": _class,
                        "attr": "ProjectID"
                    }
                )

        Database.set_no_access_check(True)
        create_task(Project.post_delete_cascade, collection_attribute_list, document.id, job_timeout=7200)
        Database.set_no_access_check(False)

    def clean(self):
        super().clean()
        count = Project.objects(NameLower=self.NameLower, id__ne=self.id).count()
        if count:
            raise ValidationError("Project name must be unique",
                                  errors={"Name": {"Value": self.Name,
                                                   "List": False,
                                                   "Message": "Project name must be unique"}})