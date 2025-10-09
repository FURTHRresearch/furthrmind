from mongoengine.base import LazyReference
from tenjin.mongo_engine import Database
from enum import Enum

class Update:

    @staticmethod
    def update(collection, attribute, value, entry_id, database=None, user_id=None,
               layout_check=False, validate=True, no_versioning=False, **kwargs):

        cls, doc = Database.get_collection_class_and_document(collection, entry_id)

        if not doc:
            return entry_id
        
        if isinstance(attribute, Enum):
            attribute = attribute.name

        old_value = doc[attribute]
        if old_value == value:
            return entry_id
        if isinstance(old_value, LazyReference):
            if old_value.id == value:
                return entry_id

        doc[attribute] = value
        if layout_check:
            doc.save()
        else:
            signal_kwargs = {
                "Opr": "Update",
                "Attr": attribute,
                "Value": value,
            }
            if no_versioning:
                signal_kwargs["NoVersioning"] = True
            if kwargs:
                signal_kwargs.update(kwargs)
            doc.save(validate=validate, signal_kwargs=signal_kwargs)
        if value is None:
            eval(f"doc.update({attribute} = None) ")
        if isinstance(value, list) & (not value):
            # string = f"add_to_set__{attribute}"
            eval(f"doc.update({attribute} = []) ")

        return entry_id
