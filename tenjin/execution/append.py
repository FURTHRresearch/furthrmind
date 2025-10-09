from tenjin.mongo_engine import Database
from enum import Enum
from bson import ObjectId
from mongoengine.base.datastructures import LazyReference


class Append:

    @staticmethod
    def append(
        collection,
        attribute,
        entry_id,
        value,
        database=None,
        user_id=None,
        validate=True,
        no_versioning=False,
        **kwargs
    ):

        cls, doc = Database.get_collection_class_and_document(collection, entry_id)

        if not doc:
            return entry_id
        
        if isinstance(attribute, Enum):
            attribute = attribute.name

        item_found = False
        for item in reversed(doc[attribute]):
            if isinstance(value, ObjectId) and isinstance(item, LazyReference):
                if value == item.id:
                    item_found = True
                    break
            elif isinstance(value, LazyReference) and isinstance(item, LazyReference):
                if value.id == item.id:
                    item_found = True
                    break
            else:
                if value == item:
                    item_found = True
                    break

        if item_found:
            return entry_id

        doc[attribute].append(value)
        signal_kwargs = {
                "Opr": "Append",
                "Attr": attribute,
                "Value": value,
            }
        if no_versioning:
            signal_kwargs["NoVersioning"] = True
        if kwargs:
            signal_kwargs.update(kwargs)
        doc.save(
            validate=validate,
            signal_kwargs={
                "Opr": "Append",
                "Attr": attribute,
                "Value": value,
            },
        )

        return entry_id
