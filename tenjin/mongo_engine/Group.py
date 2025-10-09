from mongoengine import *
from tenjin.mongo_engine.BaseClassProjectID import BaseClassProjectID
from tenjin.tasks.rq_task import create_task


class Group(BaseClassProjectID):
    meta = {
        "collection": __qualname__,
        "indexes": [
            ("_id", "GroupID"),
            ("ProjectID", "GroupID"),
            "FieldDataIDList",
            ("FieldDataIDList", "Date", "_id"),
            "GroupID",
            "ProjectID",
            "Name",
            "NameLower",
            "Date",
            "ShortID",
            ("NameLower", "ProjectID"),
            ("NameLower", "GroupID"),
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
        return "grp"

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            document.generate_short_id()

    def clean(self):
        super().clean()
        if self.GroupID:
            if not self._created:
                "There cannot be a circular dependeny if the group is just created, because it cannot be referenced by any other group"
                if self.GroupID.id == self.id:
                    raise ValidationError(
                        "Group cannot be its own parent",
                        errors={
                            "GroupID": {
                                "Value": self.GroupID,
                                "List": False,
                                "Message": "Group cannot be its own parent",
                            }
                        },
                    )
                child_group_id_list = []  # this will be all children of this group
                temp_id_list = [self.id]
                while temp_id_list:
                    child_group_id_list.extend(temp_id_list)
                    child_group_list = Group.objects(GroupID__in=temp_id_list)
                    if child_group_list:
                        temp_id_list = [
                            child_group.id for child_group in child_group_list
                        ]
                    else:
                        temp_id_list = []
                if self.GroupID.id in child_group_id_list:
                    raise ValidationError(
                        "Subgroup - Group circular dependency",
                        errors={
                            "GroupID": {
                                "Value": self.GroupID,
                                "List": False,
                                "Message": "Subgroup - Group circular dependency",
                            }
                        },
                    )

        # check uniqueness constraint, cannot be done with unique_with, because GroupID and GroupID=None behavior.
        # If you set GroupID=None and unique_with=GroupID, saving the document will fail. Thus a manual validation is required

        if self.GroupID:
            # Only items within the same parent group must be unique
            count = Group.objects(
                Q(GroupID=self.GroupID)
                & Q(NameLower=self.NameLower)
                & Q(id__ne=self.id)
            ).count()
            if count > 0:
                raise ValidationError(
                    "Group name must be unique within it's parent group",
                    errors={
                        "Name": {
                            "Value": self.Name,
                            "List": False,
                            "Message": "Group name must be unique within it's parent group",
                        }
                    },
                )
        else:
            count = Group.objects(
                Q(ProjectID=self.ProjectID)
                & Q(NameLower=self.NameLower)
                & Q(id__ne=self.id)
            ).count()
            if count > 0:
                raise ValidationError(
                    "Group name must be unique within it's parent group",
                    errors={
                        "Name": {
                            "Value": self.Name,
                            "List": False,
                            "Message": "Group name must be unique within it's parent group",
                        }
                    },
                )

    def create_method(self, kwargs):
        for attr in [Group.FileIDList]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == Group.FileIDList.name:
            from .File import File

            File.update_project_external_triggered(self.FileIDList, self.ProjectID)
        if attr == Group.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.update_fielddata_in_parent("Group", self.id)

    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == Group.FileIDList.name:
            from .File import File

            File.update_project_external_triggered([value], self.ProjectID)
        if attr == Group.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.append_fielddata_to_parent("Group", self.id, value)

    def pop_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == Group.FieldDataIDList.name:
            from .FieldData import FieldData

            FieldData.remove_fielddata_from_parent("Group", self.id, value)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        from .Experiment import Experiment
        from .Permission import Permission
        from .Sample import Sample
        from .ResearchItem import ResearchItem
        from .FieldData import FieldData

        super().post_delete_method(sender, document, **kwargs)

        collection_attribute_list = [
            {"class": Permission, "attr": Permission.GroupNoDeleteIDList.name},
            {"class": Permission, "attr": Permission.GroupNoReadIDList.name},
            {"class": Permission, "attr": Permission.GroupNoWriteIDList.name},
        ]
        Group.post_delete_pull(collection_attribute_list, document.id)

        collection_attribute_list = [
            {"class": "Group", "attr": "GroupID"},
            {"class": FieldData, "attr": FieldData.ParentDataID.name},
        ]
        Group.post_delete_cascade(collection_attribute_list, document.id)

        exps = Experiment.objects(GroupIDList__in=[document.id])
        for exp in exps:
            create_task(exp.remove_group, document.id)

        samples = Sample.objects(GroupIDList__in=[document.id])
        for sample in samples:
            create_task(sample.remove_group, document.id)

        r_items = ResearchItem.objects(GroupIDList__in=[document.id])
        for r_item in r_items:
            create_task(r_item.remove_group, document.id)

    FieldDataIDList = ListField(
        LazyReferenceField("FieldData"), default=list
    )  # reverse_delete_rule=PULL
    FieldData = ListField(EmbeddedDocumentField("FieldDataEmbedded"), default=list)
    FileIDList = ListField(LazyReferenceField("File"), default=list)
    Name = StringField(required=True)
    NameLower = StringField(required=True)
    ShortID = StringField(required=True)
    GroupID = LazyReferenceField("Group", null=True)  # , reverse_delete_rule=NULLIFY)
