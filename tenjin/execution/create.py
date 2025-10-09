from enum import Enum

from tenjin.mongo_engine import Database


class Create:

    @staticmethod
    def create(
        collection,
        parameter,
        database=None,
        userID=None,
        return_document=False,
        validate=True,
        no_versioning=False,
        **kwargs
        
    ):

        keys = list(parameter.keys())
        for key in keys:
            if isinstance(key, Enum):
                parameter[key.name] = parameter[key]
                parameter.pop(key)

        if "ProjectIDList" in parameter:
            project_id_list = parameter["ProjectIDList"]
            if project_id_list:
                project_id = project_id_list[0]
            else:
                project_id = None
            parameter["ProjectID"] = project_id
            parameter.pop("ProjectIDList")

        cls = Database.get_collection_class(collection)
        doc = cls(**parameter)
        signal_kwargs = {
                "Opr": "Create",
                "Attr": None,
                "Value": parameter,
            }
        if no_versioning:
            signal_kwargs["NoVersioning"] = True
        if kwargs:
            signal_kwargs.update(kwargs)
        doc.save(
            validate=validate,
            signal_kwargs=signal_kwargs,
        )
        if return_document:
            return doc

        return doc.id
