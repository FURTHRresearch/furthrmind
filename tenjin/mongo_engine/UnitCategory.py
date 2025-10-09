from mongoengine import *
from .BaseClassProjectIDOptional import BaseClassProjectIDOptional

class UnitCategory(BaseClassProjectIDOptional):
    meta = {"collection": __qualname__,
            "indexes": [
                "ProjectID",
                "Predefined"
            ]
            }

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .Unit import Unit

        collection_attribute_list = [
            {"class": Unit,
             "attr": Unit.UnitCategoryIDList.name},
        ]
        UnitCategory.post_delete_pull(collection_attribute_list, document.id)

    Name = StringField(required=True)
    Predefined = BooleanField(default=False)
