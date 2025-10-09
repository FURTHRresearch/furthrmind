from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID

class ResearchCategory(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "ProjectID"
            ]}

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        if flag in ["write", "delete"]:
            # only project admins can create, delete or modify fields
            flag = "invite"
        return super().check_permission(document_list, flag, user, signal_kwargs)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .ResearchItem import ResearchItem

        collection_attribute_list = [
            {"class": ResearchItem,
             "attr": ResearchItem.ResearchCategoryID.name},
        ]
        ResearchCategory.post_delete_cascade(collection_attribute_list, document.id)

    Name = StringField(required=True)
    NameLower = StringField(required=True, unique_with="ProjectID")
    Description = StringField(null=True)

