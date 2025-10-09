from mongoengine import *

from .BaseClassProjectID import BaseClassProjectID
from tenjin.cache import Cache


class ResearchItem(BaseClassProjectID):
    meta = {
        "collection": __qualname__,
        "indexes": [
            "ProjectID",
            "FieldDataIDList",
            "GroupIDList",
            "ResearchCategoryID",
            "Name",
            "NameLower",
            "Date",
            "ShortID",
            ("NameLower", "ResearchCategoryID"),
            ("NameLower", "ResearchCategoryID", "GroupIDList"),
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

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            document.generate_short_id()

    @staticmethod
    def get_prefix():
        return "rtm"

    def __setattr__(self, key, value):
        prohibited_keys = ["ResearchCategoryID"]
        permitted = self.check_prohibited_attributes(key, prohibited_keys)
        if permitted:
            super().__setattr__(key, value)

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        group = self.GroupIDList[0]
        group = group.fetch()
        self.ProjectID = group.ProjectID

    def create_method(self, kwargs):
        for attr in [ResearchItem.FileIDList]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == ResearchItem.FileIDList.name:
            from .File import File

            File.update_project_external_triggered(self.FileIDList, self.ProjectID)
        if attr == ResearchItem.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.update_fielddata_in_parent("ResearchItem", self.id)

        if attr == ResearchItem.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")
            
    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == ResearchItem.FileIDList.name:
            from .File import File

            File.update_project_external_triggered([value], self.ProjectID)
        if attr == ResearchItem.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.append_fielddata_to_parent("ResearchItem", self.id, value)
        
        if attr == ResearchItem.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")

    def pop_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == ResearchItem.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.remove_fielddata_from_parent("ResearchItem", self.id, value)

        if attr == ResearchItem.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")
            
    def clean(self):
        super().clean()
        count = ResearchItem.objects(
            NameLower=self.NameLower,
            ResearchCategoryID=self.ResearchCategoryID,
            id__ne=self.id,
        ).count()

        if count > 0:
            raise ValidationError(
                "ResearchItem name must be unique within this category",
                errors={
                    "Name": {
                        "Value": self.Name,
                        "List": False,
                        "Message": "ResearchItem name must be unique within this category",
                    }
                },
            )

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)

        from .SpreadSheet import SpreadSheet
        from .Link import Link
        from .FieldData import FieldData

        collection_attribute_list = [
            {"class": SpreadSheet, "attr": SpreadSheet.ResearchItemIDList.name}
        ]
        ResearchItem.post_delete_pull(collection_attribute_list, document.id)

        collection_attribute_list = [
            {"class": Link, "attr": Link.DataID1.name},
            {"class": Link, "attr": Link.DataID2.name},
            {"class": FieldData, "attr": FieldData.ParentDataID.name},
        ]
        ResearchItem.post_delete_cascade(collection_attribute_list, document.id)
        
        # cache must be cleaned
        cache = Cache.get_cache()
        cache.delete(f"{document.id}")
        
    def remove_group(self, group_id):
        from tenjin.execution.delete import Delete
        from tenjin.execution.pop import Pop

        if len(self.GroupIDList) > 1:
            Pop.pop("ResearchItem", "GroupIDList", self.id, group_id)
        else:
            Delete.delete("ResearchItem", self.id)

    FieldDataIDList = ListField(
        LazyReferenceField("FieldData"), default=list
    )  # , reverse_delete_rule=PULL
    FieldData = ListField(EmbeddedDocumentField("FieldDataEmbedded"), default=list)
    FileIDList = ListField(
        LazyReferenceField("File"), default=list
    )  # , reverse_delete_rule=PULL
    Name = StringField(required=True)
    # uniqueness check with clean method
    NameLower = StringField(required=True)  # unique_with="ResearchCategoryID"
    GroupIDList = ListField(
        LazyReferenceField("Group"), default=list
    )  # , reverse_delete_rule=PULL
    Neglect = BooleanField(default=False)
    Protected = BooleanField(default=False)
    ResearchCategoryID = LazyReferenceField(
        "ResearchCategory", required=True
    )  # , reverse_delete_rule=CASCADE)
    ShortID = StringField(required=True)
