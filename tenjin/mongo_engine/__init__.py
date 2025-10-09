import click
from flask import current_app, g

from mongoengine import ValidationError, Document, ListField, connect, disconnect_all
from tenjin.execution.delete import Delete

from .ImportCollections import *
from flask import Flask
from queue import Queue
from threading import Thread


class Database:
    """
    Class for init mongoengine and to operate some maintenance tasks

    """

    db = None
    handle_error_action_storage = {}

    @staticmethod
    def init_db(app: Flask):
        """
        Init the database
        Adds some commands to the cli for maintenance tasks executed from the command line

        Parameters
        ----------
        app : Flask
            instance of the Flask app
        """
        uri = app.config.get("MONGODB_URI")
        MONGODB_SETTINGS = {"host": uri}
        app.config.update({"MONGODB_SETTINGS": MONGODB_SETTINGS})

        db = connect(host=uri)

        Database.db = db
        BaseClass.init_delete_rules_and_signals()
        app.cli.add_command(Database.check_data_base_click_command)
        app.cli.add_command(Database.check_missing_db_keys_click_command)
        app.cli.add_command(Database.correct_si_values_click_command)

    @staticmethod
    def run_ensure_indexes():
        """
        Run the ensure indexes method for all collections

        Executed from the create_app method in the tenjin/__init__.py file
        """
        BaseClass.run_ensure_indexes()

    @staticmethod
    def check_for_existing_version():
        """
        Check the current version of the software from the SoftwareVersion collection

        Returns
        -------
        str
            Returns the version as a string if it exists, otherwise False
        """
        current_version = SoftwareVersion.objects().order_by("-Date").first()
        if not current_version:
            return False
        return current_version.Version

    @staticmethod
    def set_no_access_check(value):
        """
        Set the no_access_check flag in the flask g object
        This method is used for certain operations where the access check is not needed or where the access check will not allow
        the operation. For instance a change of the owner of a project. Other examples are automatic database updates for new
        software versions or enrollment and creation of new users when logged in by LDAP

        Parameters
        ----------
        value : Bool
            If true, the access check is disabled
        """
        g.no_access_check = value

    @staticmethod
    def check_for_no_access_check():
        """
        Method to check whether the no_access_check flag is set in the flask g object

        Returns
        -------
        Bool
            If true, the access check is disabled
        """
        if "no_access_check" in g:
            return g.no_access_check
        else:
            return

    @staticmethod
    def get_collection_class_and_document(
        collection: str, document_id: str = None, short_id: str = None,
        only: list = None
    ):
        """
        Method to get the collection class and the document from the database

        Parameters
        ----------
        collection : str
           Name of the collection
        document_id : str, optional
            id of the document, by default None
        short_id : str, optional
            short id of the document, by default None
        only : list, optional
            List of attributes that should be returned, by default None

        Raises
        ValueError:
            If document is not found
        ------
        Returns
        -------
        BaseClass
            Collection class
        Document:
            Document object
        """
        cls = Database.get_collection_class(collection)
        if short_id:
            doc = cls.objects(ShortID=short_id)
        else:
            doc = cls.objects(id=document_id)
        if only:
            for item in only:
                doc = doc.only(item)
        doc = doc.first()

        return cls, doc

    @staticmethod
    def get_collection_class(requested_collection: str):
        """
        Get the collection class from the collection name
        If the requested collection name is passed as plural with an "s" at the end, the method will also check for the singular form

        Parameters
        ----------
        requested_collection : str
            Name of the collection

        Returns
        -------
        BaseClass
            Collection class

        Raises
        ------
        ValueError
            If collection not found
        """
        requested_collection_list = [requested_collection, requested_collection[:-1]]
        all_collections = Database.get_all_collection_classes()
        all_collections_lower = [c.lower() for c in all_collections]
        for requested_collection in requested_collection_list:
            if not isinstance(requested_collection, str):
                if issubclass(requested_collection, BaseClass):
                    return requested_collection
            if requested_collection.lower() in all_collections_lower:
                cls = eval(
                    all_collections[
                        all_collections_lower.index(requested_collection.lower())
                    ]
                )
                return cls
        raise ValueError("Invalid collection")

    @staticmethod
    @click.command("db-layout-check")
    @click.option("--only")
    @click.option("--exclude")
    def check_data_base_click_command(only, exclude):
        """
        Click command to start the db-layout-check
        only must be a comma separated list of collections to check
        exclude must be a comma separated list of collections to exclude
        """

        if only:
            only = only.split(",")
            only = [o.replace(" ", "") for o in only]
        if exclude:
            exclude = exclude.split(",")
            exclude = [e.replace(" ", "") for e in exclude]
        Database.check_database(only, exclude)

    @staticmethod
    @click.command("check-missing-db-keys")
    def check_missing_db_keys_click_command():
        """
        Click command to start the check for missing db keys
        """
        Database.check_missing_db_keys()

    @staticmethod
    @click.command("correct-si-values")
    def correct_si_values_click_command():
        Database.correct_si_values()

    @staticmethod
    def correct_si_values():
        from tenjin import create_app

        app = create_app(minimal=True)
        with app.app_context():
            from tenjin.mongo_engine.FieldData import FieldData

            def inner(queue: Queue):
                import time

                app = create_app(minimal=True)
                with app.app_context():
                    time.sleep(3)
                    Database.set_no_access_check(True)
                    while True:
                        if queue.empty():
                            break
                        else:
                            item = queue.get()
                            fd_id = item["id"]
                            pos = item["pos"]
                            count = item["count"]
                            print(f"{pos+1} / {count}")
                            fd = FieldData.objects(id=fd_id).first()
                            fd.update_si_value()
                            if fd.Type == "NumericRange":
                                fd.update_si_value_max()
                    Database.set_no_access_check(False)

            queue = Queue()
            fielddata = FieldData.objects(Type__in=["Numeric", "NumericRange"]).only(
                "id"
            )
            count = fielddata.count()

            threadList = []
            for i in range(2):
                thread = Thread(target=inner, args=(queue,))
                threadList.append(thread)
                thread.start()

            for pos, fd in enumerate(fielddata):
                queue.put({"id": fd.id, "pos": pos, "count": count})

            for thread in threadList:
                thread.join()

    @staticmethod
    def get_all_collection_classes() -> list[str]:
        """
        Method to get all collection classes registered in the ImportCollections module

        Returns
        -------
        list[str]
            List of strings with the collection names
        """
        all_collections = dir(ImportCollections)
        result = []
        for c in all_collections:
            if c.startswith("__"):
                continue
            elif c.startswith("BaseClass"):
                continue
            result.append(c)
        return result

    @staticmethod
    def check_missing_db_keys():
        """
        Method to check for missing keys for all collections in the database
        """
        from tenjin import create_app

        app = create_app(minimal=True)
        with app.app_context():
            all_collections = dir(ImportCollections)
            for c in all_collections:
                if c.startswith("__"):
                    continue
                elif c in [
                    "BaseClass",
                    "BaseClassProjectID",
                    "BaseClassProjectIDOptional",
                ]:
                    continue
                cls = Database.get_collection_class(c)
                fields = cls._fields
                Database.check_for_all_keys(fields, c)

    @staticmethod
    def check_database(only: list = None, exclude: list = None):
        """
        Method to check the database for all collections for a) for missing keys and b) validate all documents

        Parameters
        ----------
        only : list, optional
            to check only certain collections, by default None
        exclude : list, optional
            to exclude certain collections, by default None
        """
        from tenjin import create_app
        from app import enable_maintenance_mode, disable_maintenance_mode

        app = create_app(minimal=True)
        if not only:
            only = []
        only_lower = [o.lower() for o in only]
        if not exclude:
            exclude = []
        exclude_lower = [e.lower() for e in exclude]
        with app.app_context():
            try:
                g.no_access_check = True
                enable_maintenance_mode()

                all_collections = dir(ImportCollections)

                for c in all_collections:
                    if c.startswith("__"):
                        continue
                    elif c in [
                        "BaseClass",
                        "BaseClassProjectID",
                        "BaseClassProjectIDOptional",
                    ]:
                        continue
                    if only and c.lower() not in only_lower:
                        continue
                    if c.lower() in exclude_lower:
                        print(f"Excluded: {c}")
                        continue
                    cls = Database.get_collection_class(c)
                    fields = cls._fields
                    Database.check_for_all_keys(fields, c)
                    if c == "Column":
                        docs = cls.objects().exclude("Data")
                    else:
                        docs = cls.objects()
                    print(cls)
                    total = docs.count()
                    for count, d in enumerate(docs):
                        if (count / 100).is_integer():
                            print(f"{count} / {total}")
                        Database.validate_document(d, c)
            finally:
                g.no_access_check = False
                disable_maintenance_mode()

    @staticmethod
    def check_for_all_keys(fields: list, collection_name: str):
        """
        Method to check for all keys in one collection and add them if they are missing

        Parameters
        ----------
        fields : list
            List of field names that must be present in the collection
        collection_name : str
            Name of the collection
        """
        from tenjin.database.db import get_db

        db = get_db().db
        for field, FieldType in fields.items():
            if field == "id":
                continue
            if isinstance(FieldType, ListField):
                db[collection_name].update_many(
                    {field: {"$exists": False}}, {"$set": {field: []}}
                )
            else:
                db[collection_name].update_many(
                    {field: {"$exists": False}}, {"$set": {field: None}}
                )

    @staticmethod
    def validate_document(doc: Document, collection_string: str):
        """
        Method to validate a document and handle errors

        Parameters
        ----------
        doc : Document
            The document to be validated
        collection_string : str
            The name of the collection the document belongs to
        """
        invalid_key_mapping = {}
        other_error = None
        try:
            doc.validate(clean=True)
        except Exception as e:
            if isinstance(e, ValidationError):
                invalid_key_mapping = Database.get_invalid_keys(e)
            else:
                other_error = e
        if "ProjectID" in invalid_key_mapping:
            if hasattr(doc, "update_project"):
                try:
                    doc.update_project()
                except:
                    pass
                try:
                    invalid_key_mapping = {}
                    other_error = None
                    doc.save()
                except Exception as e:
                    if isinstance(e, ValidationError):
                        invalid_key_mapping = Database.get_invalid_keys(e)
                    else:
                        other_error = e
        Database.handle_error(collection_string, doc, invalid_key_mapping, other_error)

    @staticmethod
    def get_invalid_keys(e: ValidationError):
        """
        Extracts the invalid keys from a ValidationError object. The validation error object is raised during validation
        The validation error object contains a dictionary with the invalid keys and the corresponding error messages

        Parameters
        ----------
        e : ValidationError
            The ValidationError object, that was raised during validation

        Returns
        -------
        dict
            Dictionary with the invalid keys and the corresponding error messages
        """
        invalid_key_mapping = {}
        errors = e.errors
        if "__all__" in errors:
            e_all = errors["__all__"]
            e_all_errors = e_all.errors
            if e_all_errors:
                invalid_key_mapping.update(e_all_errors)
        for key in errors:
            if key == "__all__":
                continue
            invalid_key_mapping[key] = errors[key]
        return invalid_key_mapping

    @staticmethod
    def handle_error(
        collection_string: str,
        doc: Document,
        invalid_key_mapping: dict,
        other_error: Exception,
    ):
        """
        Method to handle errors during validation of a document
        Requests user input for the error handling.

        Parameters
        ----------
        collection_string : str
            _description_
        doc : Document
            _description_
        invalid_key_mapping : dict
            _description_
        other_error : Exception
            _description_
        """

        def handle(_key):
            """
            Nested method to request user input for the error handling and return the action

            Parameters
            ----------
            _key : str
                The invalid key

            Returns
            -------
            str
                The action to be taken
            """
            value = None
            is_list = False
            message = ""
            if isinstance(invalid_key_mapping[_key], dict):
                value = invalid_key_mapping[_key]["Value"]
                is_list = invalid_key_mapping[_key]["List"]
                message = invalid_key_mapping[_key]["Message"]
            else:
                message = invalid_key_mapping[_key]
            action = Database.get_user_input_validation_error(
                collection_string, doc.id, _key, value, is_list, message
            )

            if action == "Delete":
                Delete.delete(collection_string, doc.id, layout_check=True)
                return "deleted"  # When the item is deleted, there is no need to check for furthr keys

            elif action == "Remove":
                # Remove the value from the list
                # The document will be saved after the loop
                value_for_update = doc[_key].remove(value)
                doc[_key] = value_for_update
                return "updated"
            elif action == "None":
                # Value is set to None
                # The document will be saved after the loop
                value_for_update = None
                doc[_key] = value_for_update
                return "updated"

        if invalid_key_mapping:
            deleted = False
            updated_keys = []
            for key in invalid_key_mapping:
                return_string = handle(key)
                if return_string == "deleted":
                    deleted = True
                    break
                elif return_string == "updated":
                    updated_keys.append(key)

            if not deleted:
                for key in updated_keys:
                    print(doc, key, doc[key])
                    # One update per key to have all changes in the Versioning
                    doc.save(
                        signal_kwargs={
                            "Opr": "Update",
                            "Attr": key,
                            "Value": doc[key],
                        }
                    )
                    if doc[key] is None:
                        eval(f"doc.update({key} = None) ")
                    if isinstance(doc[key], list) & (not doc[key]):
                        eval(f"doc.update({key} = []) ")

        if other_error:
            action = Database.get_user_input_other_error(
                collection_string, doc.id, other_error
            )
            if action == "Delete":
                Delete.delete(collection_string, doc.id, layout_check=True)
            else:  # action == continue
                pass

    @staticmethod
    def get_user_input_validation_error(
        collections_string: str, doc_id: str, key: str, value, is_list: bool, message
    ):
        """
        Method to request user input for the error handling and return the action
        If desired the action can be stored to proceed in the same way for all documents with the same error

        Parameters
        ----------
        collections_string : str
            Name of the collection
        doc_id : str
            Document id of the document with the error
        key : str
            Name of the field/key with the error
        value : _type_
            The current value of the field with the error
        is_list : bool
            If the value is a list
        message : str
            Error message

        Returns
        -------
        str
            The action to be taken out of: Delete, Remove, None, Continue
        """
        try:
            return Database.handle_error_action_storage[collections_string][key]
        except:
            pass

        action = ""
        valid_input = False
        while not valid_input:
            print(
                f"An entry in the collection {collections_string} is not correctly. Document_id: {doc_id}, Key: {key}"
            )
            if value:
                print(f"Value: {value}\n{message}")
            else:
                print(message)
            if is_list:
                action = input(
                    "(d)elete document, (r)emove item from attribute, (c)ontinue\n"
                )
                if action.lower() in ["d", "r", "c"]:
                    valid_input = True
            else:
                action = input(
                    "(d)elete document, (n)one, i.e. set Value to None, (c)ontinue\n"
                )
                if action.lower() in ["d", "n", "c"]:
                    valid_input = True
            if not valid_input:
                "This was not a valid return, please try again"

        valid_input = False
        store = ""
        while not valid_input:
            print(
                f"Do you want to proceed in the same way for all documents with the wrong key: {key} in collection {collections_string}?"
            )
            store = input("(y)es / (n)o\n")
            if store.lower() in ["y", "n"]:
                valid_input = True
            if not valid_input:
                "This was not a valid return, please try again"

        if store == "y":
            if action == "d":
                action = "Delete"
            elif action == "r":
                action = "Remove"
            elif action == "n":
                action = "None"
            else:
                action = "Continue"

            if collections_string not in Database.handle_error_action_storage:
                Database.handle_error_action_storage[collections_string] = {}
            Database.handle_error_action_storage[collections_string][key] = action
        return action

    @staticmethod
    def get_user_input_other_error(
        collections_string: str, doc_id: str, error: Exception
    ):
        """
        Method to request user input for the error handling for not ValidationError from mongoengine and return the action
        If desired the action can be stored to proceed in the same way for all documents with the same error

        Parameters
        ----------
        collections_string : str
            Collection name
        doc_id : str
            Document id of the document with the error
        error : Exception
            The error that was raised

        Returns
        -------
        str
            The action to be taken out of: Delete, Continue
        """
        try:
            return Database.handle_error_action_storage[collections_string][error]
        except:
            pass
        action = ""
        valid_input = False
        while not valid_input:
            print(
                f"An error was found in document {doc_id} in collection {collections_string}: {error}"
            )
            action = input("(d)elete document, (c)ontinue\n")
            if action.lower() in ["d", "c"]:
                valid_input = True
        valid_input = False

        store = ""
        while not valid_input:
            print(
                f"Do you want to proceed in the same way for all wrong documents in the collection {collections_string} "
                f"with this error: {error}?"
            )
            store = input("(y)es / (n)o\n")
            if store.lower() in ["y", "n"]:
                valid_input = True
            if not valid_input:
                "This was not a valid return, please try again"

        if store == "y":
            if action == "d":
                action = "Delete"
            else:
                action = "Continue"

            if collections_string not in Database.handle_error_action_storage:
                Database.handle_error_action_storage[collections_string] = {}
            Database.handle_error_action_storage[collections_string][
                str(error)
            ] = action

        return action


if __name__ == "__main__":
    Database.check_database()
