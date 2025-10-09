import datetime
import random
import string

import bson
import flask
import mongoengine
from bson import ObjectId
from mongoengine import *
from mongoengine import signals
from mongoengine.base.datastructures import LazyReference

from tenjin.cache import Cache
from tenjin.execution.pop import Pop
from tenjin.execution.delete import Delete

cache = Cache.get_cache()


class BaseClass(Document):
    """
    This class is the base class for all classes in the database. It contains the following fields: Date, OwnerID. Thus all
    classes will have these fields. 
    It also contains the following methods: 
        __setattr__,
        __str__,
        get_prefix,
        init_delete_rules_and_signals,
        run_ensure_indexes,
        register_signals,
        check_prohibited_attributes,
        check_permission,
        prepare_document_list_for_permission_check,
        prepare_result_permission_check,
        check_permission_to_project,
        get_permission_ids_of_user_to_project,
        get_permission_ids_of_supervisor,
        get_user,
        generate_short_id,
        post_init_method,
        update_name_lower,
        pre_save_method,
        pre_delete_method,
        post_save_method,
        post_delete_method,
        post_delete_nullify,
        post_delete_pull,
        post_delete_cascade,
        clean,
        check_lazy_refs
        
    Information to each method will be found in the docstring of the method.
    
    The baseclass is the base for each colleciton class and has methods to 
    controll the access to the document, methods that are execute before and after init, save 
    and delete of an object. This is done with signals with the bliker library.
    
    That means, every document has signals that are triggered before and after init, save and delete.
    The methods have some base functionality that is executed for all documents. Additionally, 
    each class can have its own methods that are executed
    
    For instance before a document is saved, the pre_save_method is executed. 
    This method checks if the user has the permission to save and update the document.
    
    The post_save_method is executed after the document is saved. 
    Next to other stuff it writes an entry to the versioning collection.
    
    If an object is newly created, the post_init_method is executed. It ensures,
    that the NameLower attribute is updated and the ProjectID is set. It also writes the 
    OwnerID and the Date.
    
    After Deletion the post_delete_method is executed. It writes an entry to the versioning collection.
    Post delete rules are specified in the corresponding subclasses. They used to 
    execute additional actions after a document is deleted. For instance, when a group is deleted,
    all items of the group are deleted as well.
    
    Parameters
    ----------
    Document : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    ValidationError
        _description_
    """
    Date = DateTimeField()
    OwnerID = LazyReferenceField("User", null=True)

    meta = {"abstract": True}

    # "strict": False}

    def __setattr__(self, key: str, value):
        """
        The __setattr__ method checks if the key is in the prohibited_keys list 
        ProjectID, Date, and ShortID cannot be changed and __setattr__ will not allow it.
        Additionally, if the key is "Name", the update_name_lower method is called to update 
        the NameLower field, if it exists.

        Parameters
        ----------
        key : str
            the key of the attribute to be updated
        value : 
            The value to be set
        """
        prohibited_keys = ["ProjectID", "Date", "ShortID"]
        permitted = self.check_prohibited_attributes(key, prohibited_keys)
        if permitted:
            super().__setattr__(key, value)
            if key == "Name":
                self.update_name_lower()

    def __str__(self):
        """
        The __str__ method returns the name of the class and the id of the document. It is used 
        when the object is printed.

        Returns
        -------
        str
            Class name and id
        """
        string = f"{self.__class__.__name__}"
        try:
            string += f"{self.id}"
        except:
            pass
        return string

    @staticmethod
    def get_prefix():
        """
        Some classes have a prefix that is used in the short id. 
        This method returns the prefix and is a placehoder in the 
        base class

        Returns
        -------
        str
            prefix
        """
        return ""

    @classmethod
    def init_delete_rules_and_signals(cls):
        """
        The init_delete_rules_and_signals method initializes the delete rules and signals
        for all subclasses of the class. It is called from the init_db method in the Database class.
        """
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            if subclass.__name__.startswith("BaseClass"):
                subclass.init_delete_rules_and_signals()
            if hasattr(subclass, "register_signals"):
                subclass.register_signals()
            if not subclass.__name__.startswith("BaseClass") and hasattr(subclass, "ensure_indexes"):
                try:
                    subclass.ensure_indexes()
                except:
                    print("index not created")

    @classmethod
    def run_ensure_indexes(cls):
        """
        The run_ensure_indexes method runs the ensure_indexes method for all subclasses of the class.
        """
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            if not subclass.__name__.startswith("BaseClass") and hasattr(subclass, "ensure_indexes"):
                try:
                    subclass.ensure_indexes()
                except:
                    print("index not created")

    @classmethod
    def register_signals(cls):
        """
        The register_signals method registers the signals for the class. It is called from the 
        init_delete_rules_and_signals method.
        
        post_init_method, post_save_method, pre_save_method, pre_delete_method, post_delete_method
        are connected to the corresponding signals. 
        """
        signals.post_init.connect(cls.post_init_method, sender=cls)
        signals.post_save.connect(cls.post_save_method, sender=cls)
        signals.pre_save.connect(cls.pre_save_method, sender=cls)
        signals.pre_delete.connect(cls.pre_delete_method, sender=cls)
        signals.post_delete.connect(cls.post_delete_method, sender=cls)

    def check_prohibited_attributes(self, key: str, prohibited_keys: list[str]):
        """
        Helper method to check whether a key can be changed or not.

        Parameters
        ----------
        key : str
            key to be checked
        prohibited_keys : list[str]
            List of allowed keys

        Returns
        -------
        bool
            True if allowed, False if not
        """
        permitted = True
        if key in prohibited_keys:
            if getattr(self, key) is not None:
                print(f"You cannot change {key}")
                permitted = False
        return permitted

    @classmethod
    def check_permission(cls, document_list: list, flag, user=None, signal_kwargs=None):
        """
        check_permission is a class method that checks if the user has permission to perform the
        desired action on a list of documents.
        
        
        flag 
        document_list 
        
        signal_kwargs 

        returns a list with all docs that the user has access to
            and dict {_id: True/False, ...}

        Parameters
        ----------
        document_list : list
            can be ObjectID, LazyRef or full Document: It is assumed that all
            items in the list are of the same type
        flag : str
            should be: read, write, delete, invite. It will be lowered, so it can be case-insenstive
        user : ObjectID, LazyRef or Doc, optional
            if user is None, it is taken from flask.g. If set it can be ObjectID, LazyRef or full Doc
        singla_kwargs : dict, optional
            are passed from save and delete and are necessary for updates on PermissionIDList of User and UserGroup

        Returns
        -------
        list
            List with all docs that the user has access to
        dict
            Dict with id as key and True/False for the access for each doc
        """
        
        from tenjin.mongo_engine import Database
        

        if not document_list:
            return [], {}

        # Get document list
        (document_id_list, document_list,
         document_mapping_original, document_list_original) = cls.prepare_document_list_for_permission_check(
            document_list)

        if Database.check_for_no_access_check():
            result_dict = {d_id: True for d_id in document_id_list}
            return document_list_original, result_dict

        if isinstance(document_list, mongoengine.QuerySet):
            if document_list.count() == 0:
                return [], {d_id: False for d_id in document_id_list}
        elif isinstance(document_list, list):
            if len(document_list) == 0:
                return [], {d_id: False for d_id in document_id_list}

        # --------------------------------------------------
        # get user
        from .User import User
        if user is None:
            user = flask.g.user
        if isinstance(user, LazyReference):
            user = user.fetch()
        elif isinstance(user, ObjectId):
            user = User.objects(id=user)[0]

        collection = document_list[0].__class__.__name__
        access_id_list = []
        if collection == "Project":
            for project in document_list:
                if flag.lower() == "write" and project._created:
                    # everyone can create projects
                    access_id_list.append(project.temp_id)
                else:
                    check = cls.check_permission_to_project(project.id, user.id,
                                                            flag.lower())
                    if check:
                        access_id_list.append(project.id)

        else:
            for doc in document_list:
                project = doc.ProjectID
                if project is not None:
                    # LazyRef
                    project_id = project.id
                else:
                    project_id = None
                if cls.check_permission_to_project(project_id, user.id, flag.lower()):
                    if doc._created:
                        access_id_list.append(doc.temp_id)
                    else:
                        access_id_list.append(doc.id)

        result_list, result_dict = cls.prepare_result_permission_check(
            document_id_list, access_id_list, document_mapping_original
        )

        return result_list, result_dict

    @classmethod
    def prepare_document_list_for_permission_check(cls, document_list: list):
        """
        Method to perpare the document list for the permission check. 

        Parameters
        ----------
        document_list : list
            A list of documents, either as LazyReference, ObjectId, dict or Documents

        Returns
        -------
        list
            document_id_list, list of document ids
        list
            document_list, list of documents
        dict
            document_mapping_original, mapping of document id to original document as 
            it was passed to this method
        list
            the original document_list as it was passed to this method
        """

        document_list_original = list(document_list)
        document_id_list = []
        document_mapping_original = {}

        first = document_list[0]
        if isinstance(first, LazyReference):
            id_list = [d.id for d in document_list_original]
            document_list = cls.objects(id__in=id_list)
            document_id_list = id_list
            document_mapping_original = {d.id: d for d in document_list_original}
        elif isinstance(first, ObjectId):
            id_list = document_list
            document_list = cls.objects(id__in=id_list)
            document_id_list = id_list
            document_mapping_original = {d_id: d_id for d_id in document_list_original}
        elif isinstance(first, dict):
            document_id_list = [d["_id"] for d in document_list]
            document_list = cls.objects(id__in=document_id_list)
            document_mapping_original = {d["_id"]: d for d in document_list_original}
        elif isinstance(first, Document):
            if first._created:
                # New document without id
                counter = 1
                document_id_list = []
                document_mapping_original = {}
                document_mapping = {}
                for d in document_list:
                    temp_id = counter
                    document_id_list.append(temp_id)
                    document_mapping_original[temp_id] = d
                    document_mapping[temp_id] = d
                    d.temp_id = counter
                    counter += 1
            else:
                document_id_list = [d.id for d in document_list]
                document_mapping_original = {d.id: d for d in document_list_original}

        return document_id_list, document_list, document_mapping_original, document_list_original

    @classmethod
    def prepare_result_permission_check(cls, document_id_list: list, 
                                        access_id_list: list, document_mapping_original: dict):
        """
        Method to prepare the result of the permission check.

        Parameters
        ----------
        document_id_list : list
            List of documents passed to the permission check
        access_id_list : list
            List of document ids that the user has access to
        document_mapping_original : dict
            Dict that maps document id to the original document

        Returns
        -------
        list
            list of original documents that the user has access to
        dict
            dict with document id as key and True/False for the access for each doc
        """

        result_list = []
        result_dict = {}
        for d_id in document_id_list:
            access = d_id in access_id_list
            result_dict[d_id] = access
            if access:
                doc = document_mapping_original[d_id]
                if hasattr(doc, "temp_id"):
                    delattr(doc, "temp_id")
                result_list.append(doc)

        return result_list, result_dict

    @classmethod
    @cache.memoize()
    def check_permission_to_project(cls, project_id: bson.ObjectId, user_id: str, flag:str):
        """
        Method to check if the user has permission to perform the desired action on a project.
        The method is cached in the redis db for 60 secs to have a faster access.
        Owner have always full access.
        Otherwise the access will be checked with the corresponding permission.
        
        Parameters
        ----------
        project_id : bson.ObjectId
            ID of the project
        user_id : str
            ID of the user that wants to perform the action
        flag : str
            Flag that indicates the action that the user wants to perform.
            Can be: read, write, delete, invite

        Returns
        -------
        bool
            True or False, depending on the access
        """
        from tenjin.mongo_engine import Permission
        from .Project import Project
        project = Project.objects(id=project_id).only("OwnerID").first()
        
        if project.OwnerID:
            if project.OwnerID.id == user_id:
                return True

        # look for all permission attached to the user
        p_ids = cls.get_permission_ids_of_user_to_project(project_id, user_id)
        permissions = Permission.objects(id__in=p_ids)

        if flag == "write":
            for permission in permissions:
                return permission.Write is True
            return False

        # delete
        if flag in "delete":
            for permission in permissions:
                return permission.Delete is True
            return False

        # invite
        elif flag == "invite":
            for permission in permissions:
                return permission.Invite is True
            return False

        # read
        elif flag == "read":
            for permission in permissions:
                return permission.Read is True

            p_ids = BaseClass.get_permission_ids_of_supervisor(user_id)
            permissions = Permission.objects(id__in=p_ids)
            for permission in permissions:
                if permission.ProjectID.id == project_id:
                    return permission.Read is True
            return False


    @classmethod
    @cache.memoize()
    def get_permission_ids_of_user_to_project(cls, project_id: bson.ObjectId, user_id):
        """
        Method to get the permission ids of a user to a project. 
        Direct user permissions and permissions from user groups are considered.
        The method is cached in the redis db for 60 secs to have a faster access.
        Called from check_permission_to_project and from Project class.
        
        Parameters
        ----------
        project_id : bson.ObjectId
            ID of the project
        user_id : str or ObjectId
            ID of the user

        Returns
        -------
        list
            List of ObjectIDs of the permissions
        """

        from tenjin.mongo_engine.Permission import Permission
        from tenjin.mongo_engine.UserGroup import UserGroup
        from tenjin.mongo_engine.User import User
        user = User.objects(id=user_id).only("PermissionIDList").first()

        # look for all permission attached to the user
        # getting all direct permissions
        permissions = user.PermissionIDList

        # getting all user group permissions
        user_groups = UserGroup.objects(UserIDList__in=[user.id]).only("PermissionIDList")
        for ug in user_groups:
            permissions.extend(ug.PermissionIDList)

        permissions = Permission.objects(id__in=[p.id for p in permissions],
                                         ProjectID=project_id).only("id")

        return [p.id for p in permissions]

    @classmethod
    @cache.memoize()
    def get_permission_ids_of_supervisor(cls, user_id: ObjectId):
        """
        method that returns the permission ids of a supervisor
        This method is recursive. That means, if a supervised user is also a supervisor,
        the permissions of the supervised user are considered as well. 
        If the supervised users are part of a user group, the permissions of the 
        user group are considered as well.
        The method is cached in the redis db for 60 secs to have a faster access.

        Parameters
        ----------
        user_id : ObjectId
            UserID of the supervisor

        Returns
        -------
        list
            permission ids of the supervised users and user groups the supervised 
            users are part of
        """
        from tenjin.mongo_engine.User import User
        from tenjin.mongo_engine.UserGroup import UserGroup
        from tenjin.mongo_engine.Supervisor import Supervisor
        from tenjin.mongo_engine.Permission import Permission

        sub_user_id_list = []
        parent_id_list = [user_id]
        permissions = []

        while parent_id_list:
            supervisor_list = Supervisor.objects(TopUserID__in=parent_id_list).only("SubUserID")
            # subs become new parents
            parent_id_list = [s.SubUserID.id for s in supervisor_list]
            sub_user_id_list.extend(parent_id_list)
        if sub_user_id_list:
            sub_user_list = User.objects(id__in=sub_user_id_list).only("PermissionIDList")
            permissions = []
            for user in sub_user_list:
                # getting all direct permissions
                permissions.extend(user.PermissionIDList)
            # getting all user group permissions
            user_groups = UserGroup.objects(UserIDList__in=sub_user_id_list).only("PermissionIDList")
            for ug in user_groups:
                permissions.extend(ug.PermissionIDList)
            permissions = Permission.objects(id__in=[p.id for p in permissions]).only("id")
        return [p.id for p in permissions]

    @staticmethod
    def get_user():
        """
        Helper method to get the user from flask.g

        Returns
        -------
        ObjectID
            Returns the user id or None
        """
        try:
            return flask.g.user
        except:
            return None

    def generate_short_id(self):
        """
        generates a short id for the document. 
        The short id is used for some collections and togehter mith the prefix it must be unique.
        The uniquness is checked in the method as well. 
        """
        document_class = type(self)
        prefix = document_class.get_prefix()

        while True:
            rnd = "".join(random.choice(string.ascii_lowercase + string.digits) for i in range(6))
            short_id = f"{prefix}-{rnd}"
            item = document_class.objects(ShortID=short_id).only("id").first()
            if not item:
                self.ShortID = short_id
                break

    @classmethod
    def post_init_method(cls, sender, document: Document, **kwargs):
        """
        The post_init_method is called after the document is initialized. It is 
        triggered from a signal using the blinker library. The connection is made 
        in the register_signals method.
        
        Parameters
        ----------
        sender : Collection Class
            Class of the document
        document : Document
            The document that is initialized
        """
        
        # if the documentend was newly created, that means it does not yet have an id and
        # does not yet existed in the database, the _created attribute is True
        if document._created:
            # updates the name lower attribute
            document.update_name_lower()
            # sets the ProjectID if necessary
            if hasattr(document, "update_project"):
                document.update_project()
            document.OwnerID = BaseClass.get_user()
            document.Date = datetime.datetime.now(datetime.UTC)

    def update_name_lower(self):
        """
        Checks if the document has a Name attribute and updates the NameLower attribute
        """
        if hasattr(self, "NameLower") and hasattr(self, "Name"):
            if self.Name is None:
                return
            self.NameLower = self.Name.lower()

    @classmethod
    def pre_save_method(cls, sender, document: Document, **kwargs):
        """
        The pre_save_method is called before the document is saved. It is 
        triggered from a signal using the blinker library. The connection is made 
        in the register_signals method.
        The pre_save_method checks if the user has permission to write the document.

        Parameters
        ----------
        sender : Collection calls
            Class of the document
        document : Document
            The document that is saved
        kwargs : dict
            signal_kwargs that are passed in some cases to the method

        Raises
        ------
        ValueError
            If no write permission
        """
        result_list, result_dict = cls.check_permission([document], "write", signal_kwargs=kwargs)
        if not result_list:
            raise ValueError("No permission")

    @classmethod
    def pre_delete_method(cls, sender, document, **kwargs):
        result_list, result_dict = cls.check_permission([document], "delete", signal_kwargs=kwargs)
        if not result_dict.get(document.id):
            raise ValueError("No permission")

    @classmethod
    def post_save_method(cls, sender, document, **kwargs):
        from tenjin.mongo_engine import Database
        """
        kwargs must look like this:
        {
            "Opr": Operation.Update,    # Item from Operation Enum (Create, Update, Append, Pop)
            "Attr": File.ProjectID,     # attribute of mongo_engine Class
            "Value": value
        }
        """
        if kwargs.get("Opr") is None:
            if Database.check_for_no_access_check():
                # if get_from_redis("LayoutCheck") == "1":
                kwargs["Opr"] = "Update due to LayoutCheck"
                kwargs["Attr"] = None
                kwargs["Value"] = None
            else:
                kwargs["Opr"] = "Update due to reverse delete role"
                kwargs["Attr"] = None
                kwargs["Value"] = None

        operation = kwargs.get("Opr")
        if operation == "Create":
            if hasattr(document, "create_method"):
                document.create_method(kwargs)
        if operation == "Update":
            value = kwargs.get("Value")
            attr = kwargs.get("Attr")
            if value is None:
                eval(f"document.update({attr} = None) ")
            if isinstance(value, list) & (not value):
                # string = f"add_to_set__{attribute}"
                eval(f"document.update({attr} = []) ")
            if hasattr(document, "update_method"):
                document.update_method(kwargs)

        if operation == "Append":
            if hasattr(document, "append_method"):
                document.append_method(kwargs)
        if operation == "Pop":
            attr = kwargs.get("Attr")
            if not document[attr]:
                eval(f"document.update({attr} = []) ")
            if hasattr(document, "pop_method"):
                document.pop_method(kwargs)

        from .Versioning import Versioning
        if cls.__name__ != "Versioning":
            if "NoVersioning" in kwargs:
                if kwargs["NoVersioning"]:
                    return
            Versioning.add_entry(document, kwargs)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        """
        kwargs must look like this:
        {
            "Opr": Operation.Delete,    # Item from Operation Enum (Create, Update, Append, Pop)
            "Attr": "",     # attribute of mongo_engine Class
            "Value": None
        }
        """
        # operation = kwargs.get("Opr")
        # if operation == "Create":
        #     if hasattr(document, "create_method"):
        #         document.create_method(kwargs)
        # if operation == "Update":
        #     if hasattr(document, "update_method"):
        #         document.update_method(kwargs)
        # if operation == "Append":
        #     if hasattr(document, "append_method"):
        #         document.append_method(kwargs)
        # if operation == "Pop":
        #     if hasattr(document, "pop_method"):
        #         document.pop_method(kwargs)

        from .Versioning import Versioning
        from tenjin.mongo_engine import Database
        if cls.__name__ != "Versioning":
            if not kwargs:
                if Database.check_for_no_access_check():
                    # if get_from_redis("LayoutCheck") == "1":
                    kwargs["Opr"] = "Delete due to LayoutCheck"
                    kwargs["Attr"] = None
                    kwargs["Value"] = None
                else:
                    kwargs["Opr"] = "Delete due to reverse delete role"
                    kwargs["Attr"] = None
                    kwargs["Value"] = None
            Versioning.add_entry(document, kwargs)

    @staticmethod
    def post_delete_nullify(collection_attribute_list, document_id):
        """
        document_id used in eval statement
        collection_attribute_list: [{"class": cls, "attr": Attriubte name},...]
        """
        from tenjin.execution.update import Update
        for mapping in collection_attribute_list:
            class_ = mapping["class"]
            attr = mapping["attr"]
            items = eval(f"class_.objects({attr}=document_id).only('id')")
            item_id_list = [i.id for i in items]
            for item_id in item_id_list:
                Update.update(class_.__name__, attr, None, item_id, validate=False)

    @staticmethod
    def post_delete_pull(collection_attribute_list, document_id):
        """
        document_id used in eval statement
        collection_attribute_list: [{"class": cls, "attr": Attriubte name},...]
        """

        for mapping in collection_attribute_list:
            class_ = mapping["class"]
            attr = mapping["attr"]
            items = eval(f"class_.objects({attr}__in=[document_id]).only('id')")
            item_id_list = [i.id for i in items]
            for item_id in item_id_list:
                Pop.pop(class_.__name__, attr, item_id, document_id, validate=False)

    @staticmethod
    def post_delete_cascade(collection_attribute_list, document_id):
        """
        document_id used in eval statement
        collection_attribute_list: [{"class": cls, "attr": Attriubte name},...]
        """
        from tenjin.mongo_engine import Database

        for mapping in collection_attribute_list:
            class_ = mapping["class"]
            if isinstance(class_, str):
                class_ = Database.get_collection_class(class_)
            attr = mapping["attr"]
            items = eval(f"class_.objects({attr}=document_id).only('id')")
            item_id_list = [i.id for i in items]
            for item_id in item_id_list:
                Delete.delete(class_.__name__, item_id)

    def clean(self):
        self.check_lazy_refs()

    def check_lazy_refs(self):
        from tenjin.mongo_engine import Database
        errors = {}
        for field in self._fields:
            if not self[field]:
                continue
            if isinstance(self._fields[field], LazyReferenceField):
                cls = Database.get_collection_class(f"{self[field].collection}")
                items = cls.objects(id=self[field].id).only("id")
                if items.count() == 0:
                    errors[field] = {"Value": self[field],
                                     "List": False,
                                     "Message": f"{self[field]} not a valid reference for {field}"}

            elif isinstance(self._fields[field], ListField):
                list_field = self._fields[field]
                if isinstance(list_field.field, LazyReferenceField):
                    cls = Database.get_collection_class(f"{self[field][0].collection}")
                    item_id_list = [item.id for item in self[field]]
                    db_items = cls.objects(id__in=item_id_list).only("id")
                    if len(item_id_list) > db_items.count():
                        db_items_id = [item.id for item in db_items]
                        for item in self[field]:
                            if item.id not in db_items_id:
                                errors[field] = {"Value": item,
                                                 "List": True,
                                                 "Message": f"{item} not a valid reference for {field}"}

        if errors:
            raise ValidationError("Errors found", errors=errors)
