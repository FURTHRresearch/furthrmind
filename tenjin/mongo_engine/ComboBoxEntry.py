from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID


class ComboBoxEntry(BaseClassProjectID):
    meta = {
        "collection": __qualname__,
        "indexes": [
            "FieldID",
            "ProjectID",
            {
                "fields": ("FieldData.FieldID", "FieldData.ValueLower"),
                "name": "field_valuelower",
            },
            {"fields": ("FieldData.FieldID", "FieldData.Value"), "name": "field_value"},
            {
                "fields": ("FieldData.FieldID", "FieldData.SIValue"),
                "name": "field_sivalue",
            },
        ],
    }

    def __setattr__(self, key, value):
        prohibited_keys = ["FieldID"]
        permitted = self.check_prohibited_attributes(key, prohibited_keys)
        if permitted:
            super().__setattr__(key, value)

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        if flag in ["write", "delete"]:
            # only project admins can create, delete or modify combobox entries
            flag = "invite"
        return super().check_permission(document_list, flag, user, signal_kwargs)

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        field = self.FieldID.fetch()
        self.ProjectID = field.ProjectID

    def create_method(self, kwargs):
        for attr in [ComboBoxEntry.FileIDList]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == ComboBoxEntry.FileIDList.name:
            from .File import File

            File.update_project_external_triggered(self.FileIDList, self.ProjectID)
        if attr == ComboBoxEntry.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.update_fielddata_in_parent("ComboBoxEntry", self.id)

    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == ComboBoxEntry.FileIDList.name:
            from .File import File

            File.update_project_external_triggered([value], self.ProjectID)
        if attr == ComboBoxEntry.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.append_fielddata_to_parent("ComboBoxEntry", self.id, value)

    def pop_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == ComboBoxEntry.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.remove_fielddata_from_parent("ComboBoxEntry", self.id, value)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .FieldData import FieldData

        collection_attribute_list = [{"class": FieldData, "attr": FieldData.Value.name}]
        ComboBoxEntry.post_delete_nullify(collection_attribute_list, document.id)

        collection_attribute_list = [
            {"class": FieldData, "attr": FieldData.ParentDataID.name},
        ]
        ComboBoxEntry.post_delete_cascade(collection_attribute_list, document.id)

    Name = StringField(required=True)
    NameLower = StringField(required=True, unique_with=["FieldID"])
    FieldDataIDList = ListField(
        LazyReferenceField("FieldData"), default=list
    )  # , reverse_delete_rule=PULL
    FieldData = ListField(EmbeddedDocumentField("FieldDataEmbedded"), default=list)
    FieldID = LazyReferenceField(
        "Field", required=True
    )  # , reverse_delete_rule=CASCADE)
    FileIDList = ListField(
        LazyReferenceField("File"),
        default=list,
    )  # , reverse_delete_rule=PULL
