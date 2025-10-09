from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID

class Notebook(BaseClassProjectID):
    meta = {"collection": __qualname__}

    # def clean(self):
    #     if self.TargetCollection is None and self.ProjectID is None:
    #         return ValidationError("ProjectID and TargetCollection cannot be None both")


    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)

        from .FieldData import FieldData
        collection_attribute_list = [
            {"class": FieldData,
             "attr": FieldData.Value.name}
        ]
        Notebook.post_delete_nullify(collection_attribute_list, document.id)

    Content = StringField(null=True)
    FileIDList = ListField(LazyReferenceField("File"), default=list)    # reverse_delete_rule=PULL
    ImageFileIDList = ListField(LazyReferenceField("File"), default=list)   # , reverse_delete_rule=PULL
