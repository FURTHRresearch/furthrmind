from mongoengine import *

from .BaseClassProjectID import BaseClassProjectID
from tenjin.cache import Cache


class Sample(BaseClassProjectID):
    meta = {
        "collection": __qualname__,
        "indexes": [
            "ProjectID",
            "FieldDataIDList",
            "GroupIDList",
            "ShortID",
            "SampleID",
            "NameLower",
            "Date",
            ("NameLower", "GroupIDList"),
            ("NameLower", "ProjectID"),
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

    @staticmethod
    def get_prefix():
        return "smp"

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            document.generate_short_id()

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        group = self.GroupIDList[0]
        group = group.fetch()
        self.ProjectID = group.ProjectID

    def clean(self):
        super().clean()
        if self.SampleID:
            if self.SampleID.id == self.id:
                raise ValidationError(
                    "Sample cannot be its own parent",
                    errors={
                        "SampleID": {
                            "Value": self.SampleID,
                            "List": False,
                            "Message": "Sample cannot be its own parent",
                        }
                    },
                )
            child_sample_id_list = []  # this will be all children of this sample
            temp_id_list = [self.id]
            while temp_id_list:
                child_sample_id_list.extend(temp_id_list)
                child_sample_list = Sample.objects(SampleID__in=temp_id_list)
                if child_sample_list:
                    temp_id_list = [
                        child_sample.id for child_sample in child_sample_list
                    ]
                else:
                    temp_id_list = []
            if self.SampleID.id in child_sample_id_list:
                raise ValidationError(
                    "Subsample - Sample circular dependency",
                    errors={
                        "SampleID": {
                            "Value": self.SampleID,
                            "List": False,
                            "Message": "Subsample - Sample circular dependency",
                        }
                    },
                )

        count = Sample.objects(
            NameLower=self.NameLower, ProjectID=self.ProjectID, id__ne=self.id
        ).count()
        if count > 0:
            raise ValidationError(
                "Sample name must be unique within this project",
                errors={
                    "Name": {
                        "Value": self.Name,
                        "List": False,
                        "Message": "Sample name must be unique within this project",
                    }
                },
            )

    def create_method(self, kwargs):
        for attr in [Sample.FileIDList]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == Sample.FileIDList.name:
            from .File import File

            File.update_project_external_triggered(self.FileIDList, self.ProjectID)
        if attr == Sample.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.update_fielddata_in_parent("Sample", self.id)
            
        if attr == Sample.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")

    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == Sample.FileIDList.name:
            from .File import File

            File.update_project_external_triggered([value], self.ProjectID)
        if attr == Sample.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.append_fielddata_to_parent("Sample", self.id, value)

        if attr == Sample.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")

    def pop_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == Sample.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.remove_fielddata_from_parent("Sample", self.id, value)

        if attr == Sample.GroupIDList.name:
            # if group changes, cache must be reseted
            cache = Cache.get_cache()
            cache.delete(f"{self.id}")

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        from .Link import Link
        from .SpreadSheet import SpreadSheet
        from .FieldData import FieldData

        super().post_delete_method(sender, document, **kwargs)

        collection_attribute_list = [{"class": Sample, "attr": "SampleID"}]
        Sample.post_delete_nullify(collection_attribute_list, document.id)

        collection_attribute_list = [
            {"class": SpreadSheet, "attr": SpreadSheet.SampleIDList.name}
        ]
        Sample.post_delete_pull(collection_attribute_list, document.id)

        collection_attribute_list = [
            {"class": Link, "attr": Link.DataID1.name},
            {"class": Link, "attr": Link.DataID2.name},
            {"class": FieldData, "attr": FieldData.ParentDataID.name},
        ]
        Sample.post_delete_cascade(collection_attribute_list, document.id)
        
        # Cache must be cleaned
        cache = Cache.get_cache()
        cache.delete(f"{document.id}")
        
        
    def remove_group(self, group_id):
        from tenjin.execution.delete import Delete
        from tenjin.execution.pop import Pop

        if len(self.GroupIDList) > 1:
            Pop.pop("Sample", "GroupIDList", self.id, group_id)
        else:
            Delete.delete("Sample", self.id)

    FieldDataIDList = ListField(
        LazyReferenceField("FieldData"), default=list
    )  # , reverse_delete_rule=PULL
    FieldData = ListField(EmbeddedDocumentField("FieldDataEmbedded"), default=list)
    FileIDList = ListField(
        LazyReferenceField("File"), default=list
    )  # reverse_delete_rule=PULL
    Name = StringField(required=True)
    NameLower = StringField(required=True, unique_with="ProjectID")
    GroupIDList = ListField(
        LazyReferenceField("Group"), default=list
    )  # reverse_delete_rule=PULL
    Neglect = BooleanField(default=False)
    Protected = BooleanField(default=False)
    ShortID = StringField(required=True)
    SampleID = LazyReferenceField("self", null=True)  # , reverse_delete_rule=NULLIFY)
