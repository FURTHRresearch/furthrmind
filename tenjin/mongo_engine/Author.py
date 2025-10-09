from mongoengine import *

from .BaseClass import BaseClass


class Author(BaseClass):
    meta = {"collection": __qualname__,
            "indexes": [
                "UserID"
            ]}

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        return document_list, {doc.id: True for doc in document_list}

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .FieldData import FieldData
        collection_attribute_list = [
            {"class": FieldData,
             "attr": FieldData.AuthorID.name}
        ]
        Author.post_delete_nullify(collection_attribute_list, document.id)

    def __setattr__(self, key, value):
        avoid = False
        if key == "UserID":
            if self.UserID is not None:
                print(f"You cannot change {key}")
                avoid = True
        if avoid:
            return
        super().__setattr__(key, value)

    def clean(self):
        super().clean()
        if not self.UserID:
            docs = Author.objects(NameLower=self.NameLower, Institution=self.Institution)
            if self._created:
                if hasattr(self, "id"):  # for layout check:
                    for doc in docs:
                        if doc.id != self.id:
                            raise ValidationError("Name and Institution must be unique",
                                                  errors={"Name": {"Value": self.Name,
                                                                   "List": False,
                                                                   "Message": "Name and Institution must be unique"}})
                elif docs.count() > 0:
                    raise ValidationError("Name and Institution must be unique",
                                          errors={"Name": {"Value": self.Name,
                                                           "List": False,
                                                           "Message": "Name and Institution must be unique"}})
            else:
                for doc in docs:
                    if doc.id != self.id:
                        raise ValidationError("Name and Institution must be unique",
                                              errors={"Name": {"Value": self.Name,
                                                               "List": False,
                                                               "Message": "Name and Institution must be unique"}})

    Name = StringField(null=True)
    Institution = StringField(null=True)
    UserID = LazyReferenceField("User", null=True)
    NameLower = StringField(null=True)  # , reverse_delete_rule=CASCADE)
