import os

import bcrypt
import bson
import flask
from bson import ObjectId
from mongoengine import *
from mongoengine.base.datastructures import LazyReference

from tenjin.tasks.rq_task import create_task
from .BaseClass import BaseClass


class User(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                "Email",
                "PermissionIDList",
                "UserName"
            ]}

    Admin = BooleanField(default=False)
    Customer = StringField(null=True)
    Email = EmailField(required=True, unique=True)
    Password = StringField(default=os.urandom(16).hex())
    FirstName = StringField(null=True)
    LastName = StringField(null=True)
    Active = BooleanField(default=True)
    ImageFileID = LazyReferenceField("File", null=True)
    PermissionIDList = ListField(LazyReferenceField("Permission"), default=list)
    UserName = StringField(null=True)

    def __setattr__(self, key, value):
        if key == "Email":
            if isinstance(value, str):
                value = value.lower()

        super().__setattr__(key, value)

    @staticmethod
    def hash_pw(pw):
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            document.lower_email_address()
            if document.Password is None:
                password = os.urandom(16).hex()
                password = User.hash_pw(password)
            else:
                password = User.hash_pw(document.Password)
            document.Password = password

    def lower_email_address(self):
        self.Email = self.Email.lower()

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        """
        everybody can create a user without permissions, otherwise self registration is not possible
        everybody can read user information
        only admin and user itself can update user information
        admins and user with invite access to certain project can add permissions
        """
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

        operation = attribute = None
        if signal_kwargs is not None:
            operation = signal_kwargs.get("Opr", None)
            attribute = signal_kwargs.get("Attr", None)

        if operation is None:
            operation = "Create"

        if operation == "Create":
            # everyone can create new user, otherwise signup would not be possible
            return document_list, {doc_id: True for doc_id in doc_id_list}

        # get user
        if user is None:
            user = flask.g.user
        if isinstance(user, LazyReference):
            user = user.fetch()
        elif isinstance(user, ObjectId):
            user = User.objects(id=user)[0]

        if operation in ["Update", "Append"]:
            if user["Admin"]:
                return document_list, {doc_id: True for doc_id in doc_id_list}

            if attribute == "PermissionIDList":
                # check if current user has access to permission, if so he is allowed to append the permission to another user
                permission_id = signal_kwargs.get("Value")
                permission_id_list, permission_result_dict = (
                    Permission.check_permission([permission_id], "invite", user)
                )
                return permission_id_list, permission_result_dict

            else:
                for doc in document_list:
                    if doc.id != user.id:
                        return [], {doc_id: False for doc_id in doc_id_list}
                return document_list, {doc_id: True for doc_id in doc_id_list}

        elif operation == "Pop":
            if attribute == "PermissionIDList":
                # check if current user has access to permission, if so he is allowed to append the permission to another user
                permission_id = signal_kwargs.get("Value")
                permission = Permission.objects(id=permission_id).first()
                if permission is None:
                    # permission already deleted => post remove from user object => allow operation
                    return document_list, {doc_id: True for doc_id in doc_id_list}

                permission_id_list, permission_result_dict = (
                    Permission.check_permission([permission_id], "invite", user)
                )
                return permission_id_list, permission_result_dict

            if user["Admin"]:
                return document_list, {doc_id: True for doc_id in doc_id_list}
            else:
                return [], {doc_id: False for doc_id in doc_id_list}

        elif operation == "Delete":
            if user["Admin"]:
                return document_list, {doc_id: True for doc_id in doc_id_list}
            else:
                return [], {doc_id: False for doc_id in doc_id_list}

    @classmethod
    def pre_save_method(cls, sender, document, **kwargs):
        super().pre_save_method(sender, document, **kwargs)

        operation = kwargs.get("Opr")
        if operation == "Update":
            value = kwargs.get("Value")
            attr = kwargs.get("Attr")
            if attr == "Password":
                value = User.hash_pw(value)
                document[attr] = value
        elif operation == "Create":
            password = document.Password
            password = User.hash_pw(password)
            document.Password = password

    def create_method(self, kwargs):
        from tenjin.execution.create import Create
        from tenjin.execution.append import Append
        from tenjin.mongo_engine.Project import Project
        from tenjin.mongo_engine.UserGroup import UserGroup

        from tenjin.database.db import get_db
        from tenjin.web.helper.email_helper import send_email

        data = {
            "UserID": self.id,
            "Name": self.Email,
        }
        Create.create("Author", data)

        token = str(os.urandom(16).hex())
        get_db().db.PasswordReset.insert_one(
            {'email': self.Email, 'token': token})

        link = flask.current_app.config['ROOT_URL'] + \
               '/set-password?token=' + token

        body = flask.render_template('emails/new_account.html', email=self.Email, link=link)


        create_task(send_email, self.Email, 'FURTHRmind account', body)

        # add permission to mask project
        mask_project = Project.objects(NameLower="maskentests_1").first()
        if mask_project:
            if mask_project["Info"] is not None:
                if mask_project["Info"].startswith("Discrepancy of particle"):
                    permissionId = Create.create("Permission",
                                                 {
                                                     "ProjectID": mask_project.id,
                                                     "Read": True,
                                                     "Write": True,
                                                     "Delete": True,
                                                     "Invite": True
                                                 })
                    Append.append("User", "PermissionIDList", self.id, permissionId, get_db(),
                                  mask_project["OwnerID"].id)

        # add user to everybody usergroup
        everybody_user_group = UserGroup.objects(NameLower="everybody").first()

        if everybody_user_group:
            Append.append("UserGroup", "UserIDList", everybody_user_group.id, self.id,
                          get_db(), everybody_user_group["OwnerID"].id)

    def append_method(self, kwargs):
        from tenjin.mongo_engine.Permission import Permission
        from tenjin.web.helper.email_helper import send_email

        user_id = flask.g.user
        if not user_id:
            email = "Someone"
        else:
            user = User.objects(id=bson.ObjectId(user_id)).first()
            email = user.Email

        if kwargs.get("Attr") == "PermissionIDList":
            permission_id = kwargs.get("Value")
            permission = Permission.objects(id=permission_id).first()
            project = permission.ProjectID.fetch()

            root_url = flask.current_app.config.get("ROOT_URL")
            link = f"{root_url}/projects/{project.id}/data"

            body = flask.render_template('emails/project_invite.html', email=email,
                                         project=project.Name,
                                         link=link)
            create_task(send_email, self.Email, 'FURTHRmind: Invite to Project', body)

    @classmethod
    def pre_delete_method(cls, sender, document, **kwargs):
        if document.Admin:
            user = User.objects(id__ne=document.id, Admin=True)
            if user.count() == 0:
                raise ValueError("You cannot delete the last admin")
        super().pre_delete_method(sender, document, **kwargs)


    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .UserGroup import UserGroup
        from .Author import Author
        from .Supervisor import Supervisor
        from .Project import Project
        from tenjin.mongo_engine import Database
        from tenjin.execution.update import Update
        from tenjin.execution.create import Create
        from tenjin.execution.append import Append

        # transfer projects
        try:
            # To avoid access problems
            Database.set_no_access_check(True)
            # transfer projects to admins
            projects = Project.objects(OwnerID=document.id)
            user = User.objects(Admin=True)
            try:
                current_user = flask.g.user
            except:
                current_user = None

            owner_changed = False
            for u in user:
                if u.id == document.id:
                    continue
                if u.id == current_user:
                    # current user becomes owner
                    for project in projects:
                        Update.update("Project", "OwnerID",
                                      u.id, project.id)
                        owner_changed = True

                else:
                    for project in projects:
                        datadict = {
                            "ProjectID": bson.ObjectId(project.id),
                            "Write": True,
                            "Read": True,
                            "Delete": True,
                            "Invite": True
                        }
                        permission_id = Create.create("Permission", datadict)
                        Append.append("User", "PermissionIDList", u.id, permission_id)

            if not owner_changed:
                u = User.objects(id__ne=document.id, Admin=True).first()
                for project in projects:
                    Update.update("Project", "OwnerID",
                                  u.id, project.id)

            # Project get Archived
            for project in projects:
                if project.Archived:
                    continue
                Update.update("Project", "Archived", True, project.id)

        except Exception as e:
            raise e
        finally:
            Database.set_no_access_check(False)

        # transfer usergroups
        try:
            usergroups = UserGroup.objects(OwnerID=document.id)
            if usergroups.count() != 0:
                if current_user:
                    new_owner = current_user
                else:
                    u = User.objects(id__ne=document.id, Admin=True).first()
                    new_owner = u.id
                Database.set_no_access_check(True)

                for ug in usergroups:
                    Update.update("UserGroup", "OwnerID", new_owner, ug.id)
        except:
            pass
        finally:
            Database.set_no_access_check(False)

        collection_attribute_list = []
        all_classes = Database.get_all_collection_classes()
        for class_string in all_classes:
            _class = Database.get_collection_class(class_string)
            if hasattr(_class, "OwnerID"):
                collection_attribute_list.append({"class": _class, "attr": "OwnerID"})

        Database.set_no_access_check(True)
        create_task(User.post_delete_nullify, collection_attribute_list, document.id)
        Database.set_no_access_check(False)

        collection_attribute_list = [
            {"class": UserGroup, "attr": UserGroup.UserIDList.name},
        ]

        Database.set_no_access_check(True)
        User.post_delete_pull(collection_attribute_list, document.id)
        Database.set_no_access_check(False)

        collection_attribute_list = [
            {"class": Author, "attr": Author.UserID.name},
            {"class": Supervisor, "attr": Supervisor.TopUserID.name},
            {"class": Supervisor, "attr": Supervisor.SubUserID.name},
        ]

        Database.set_no_access_check(True)
        create_task(User.post_delete_cascade, collection_attribute_list, document.id)
        Database.set_no_access_check(False)

        # document.post_delete_cascade(collection_attribute_list, disable_access_check=True)
