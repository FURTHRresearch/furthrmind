from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID

class Table(BaseClassProjectID):
    # todo implement
    meta = {"collection": __qualname__}

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)

        from .FieldData import FieldData
        collection_attribute_list = [
            {"class": FieldData,
             "attr": FieldData.Value.name}
        ]
        Table.post_delete_nullify(collection_attribute_list, document.id)

    Name = StringField(required=True)
    ColumnIDList = ListField(LazyReferenceField("Column"), default=list)  # reverse_delete_rule=PULL
