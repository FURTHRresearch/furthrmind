from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID
from tenjin.cache import Cache


class Experiment(BaseClassProjectID):
    meta = {
        "collection": __qualname__,
        "indexes": [
            {"name": "GroupIDList", "fields": ("GroupIDList",)},
            {"name": "ProjectID", "fields": ("ProjectID",)},
            {
                "name": "project_fielddata_date",
                "fields": ("ProjectID", "FieldDataIDList", "Date"),
            },
            {"name": "id_fielddata_date", "fields": ("_id", "FieldDataIDList", "Date")},
            "FieldDataIDList",
            "ShortID",
            "Name",
            "NameLower",
            "Date",
            "FieldData",
            {"name": "project_namelower", "fields": ("NameLower", "ProjectID")},
            {"name": "group_namelower", "fields": ("NameLower", "GroupIDList")},
            {"fields": ("FieldData.FieldID", "FieldData.ValueLower"), "name": "field_valuelower"},
            {"fields": ("FieldData.FieldID", "FieldData.Value"), "name": "field_value"},
            {"fields": ("FieldData.FieldID", "FieldData.Value", "Date"), "name": "field_value_date"},
            {"fields": ("FieldData.FieldID", "FieldData.SIValue"), "name": "field_sivalue"},
        ],
    }

    @staticmethod
    def get_prefix():
        return "exp"

    @staticmethod
    def validate_group(group_list):
        if len(group_list) == 0:
            raise ValidationError(
                "GroupIDList cannot be empty",
                errors={
                    "GroupIDList": {
                        "Value": [],
                        "List": False,
                        "Message": "GroupIDList cannot be empty",
                    }
                },
            )

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            document.generate_short_id()

    def clean(self):
        super().clean()
        count = Experiment.objects(
            NameLower=self.NameLower, ProjectID=self.ProjectID, id__ne=self.id
        ).count()
        if count:
            raise ValidationError(
                "Experiment name must be unique within this project",
                errors={
                    "Name": {
                        "Value": self.Name,
                        "List": False,
                        "Message": "Experiment name must be unique within this project",
                    }
                },
            )

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        group = self.GroupIDList[0]
        group = group.fetch()
        self.ProjectID = group.ProjectID

    def create_method(self, kwargs):
        for attr in [Experiment.FileIDList]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr:
            return
        if attr == Experiment.FileIDList.name:
            from .File import File

            File.update_project_external_triggered(self.FileIDList, self.ProjectID)
        if attr == Experiment.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.update_fielddata_in_parent("Experiment", self.id)
        
        if attr == Experiment.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")


    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == Experiment.FileIDList.name:
            from .File import File

            File.update_project_external_triggered([value], self.ProjectID)
        if attr == Experiment.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.append_fielddata_to_parent("Experiment", self.id, value)
            
        if attr == Experiment.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")


    def pop_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == Experiment.FieldDataIDList.name:
            from .FieldData import FieldData
            FieldData.remove_fielddata_from_parent("Experiment", self.id, value)

        if attr == Experiment.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")
            
    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)

        from .SpreadSheet import SpreadSheet
        from .RawData import RawData
        from .Link import Link
        from .FieldData import FieldData

        collection_attribute_list = [
            {"class": SpreadSheet, "attr": SpreadSheet.ExperimentIDList.name},
        ]
        Experiment.post_delete_pull(collection_attribute_list, document.id)

        collection_attribute_list = [
            {"class": RawData, "attr": RawData.ExpID.name},
            {"class": Link, "attr": Link.DataID1.name},
            {"class": Link, "attr": Link.DataID2.name},
            {"class": FieldData, "attr": FieldData.ParentDataID.name},
        ]
        Experiment.post_delete_cascade(collection_attribute_list, document.id)
        
        # cache must be cleaned
        cache = Cache.get_cache()
        cache.delete(f"{document.id}")

    def remove_group(self, group_id):
        from tenjin.execution.delete import Delete
        from tenjin.execution.pop import Pop

        if len(self.GroupIDList) > 1:
            Pop.pop("Experiment", "GroupIDList", self.id, group_id)
        else:
            Delete.delete("Experiment", self.id)

    FieldDataIDList = ListField(
        LazyReferenceField("FieldData"), default=list
    )  # , reverse_delete_rule=PULL
    FieldData = ListField(EmbeddedDocumentField("FieldDataEmbedded"), default=list)
    FileIDList = ListField(
        LazyReferenceField("File"), default=list
    )  # , reverse_delete_rule=PULL
    Name = StringField(required=True)
    NameLower = StringField(required=True, unique_with="ProjectID")
    GroupIDList = ListField(
        LazyReferenceField("Group"), validation=validate_group
    )  # , reverse_delete_rule=PULL
    Neglect = BooleanField(default=False)
    Protected = BooleanField(default=False)
    ShortID = StringField(required=True)
