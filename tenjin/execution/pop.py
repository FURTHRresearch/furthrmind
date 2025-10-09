from enum import Enum
from bson import ObjectId
from mongoengine.base.datastructures import LazyReference


class Pop:

    @staticmethod
    def pop(
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
        from tenjin.mongo_engine import Database

        cls, doc = Database.get_collection_class_and_document(collection, entry_id)
        if not doc:
            return entry_id
        
        if isinstance(attribute, Enum):
            attribute = attribute.name

        if len(doc[attribute]) == 0:
            return entry_id

        for item in reversed(doc[attribute]):
            if isinstance(value, ObjectId) and isinstance(item, LazyReference):
                if value == item.id:
                    doc[attribute].remove(item)
                    break
            elif isinstance(value, LazyReference) and isinstance(item, LazyReference):
                if value.id == item.id:
                    doc[attribute].remove(item)
                    break
            else:
                if value == item:
                    doc[attribute].remove(item)
                    break
                
        signal_kwargs = {
            "Opr": "Pop",
            "Attr": attribute,
            "Value": value,
        }
        if no_versioning:
            signal_kwargs["NoVersioning"] = True
        if kwargs:
            signal_kwargs.update(kwargs)
        doc.save(validate=validate, signal_kwargs=signal_kwargs)

        if not doc[attribute]:
            eval(f"doc.update({attribute} = []) ")

        return entry_id
