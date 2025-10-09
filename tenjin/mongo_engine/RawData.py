from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID
from tenjin.execution.delete import Delete

class RawData(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "ExpID",
                "ColumnIDList",
                "SampleID",
                "ResearchItemID",
                "Name"
            ]}

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            if not document.Name:
                document.Name = "Data table"

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        if self.ExpID:
            exp = self.ExpID.fetch()
            self.ProjectID = exp.ProjectID
        elif self.SampleID:
            sample = self.SampleID.fetch()
            self.ProjectID = sample.ProjectID
        elif self.ResearchItemID:
            ri = self.ResearchItemID.fetch()
            self.ProjectID = ri.ProjectID

    def create_method(self, kwargs):
        for attr in [RawData.ColumnIDList]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == RawData.ColumnIDList.name:
            from .Column import Column
            Column.update_project_external_triggered(self.ColumnIDList, self.ProjectID)

    def append_method(self, kwargs):
        attr = kwargs.get("Attr")
        value = kwargs.get("Value")
        if not attr or not value:
            return
        if attr == RawData.ColumnIDList.name:
            from .Column import Column
            Column.update_project_external_triggered([value], self.ProjectID)

    @classmethod
    def pre_delete_method(cls, sender, document, **kwargs):
        super().pre_delete_method(sender, document, **kwargs)

        from tenjin.execution import delete
        column_id_list = [c.id for c in document.ColumnIDList]
        for c_id in column_id_list:
            Delete.delete("Column", c_id)

    Name = StringField(null=True)
    ExpID = LazyReferenceField("Experiment", null=True)  # , reverse_delete_rule=CASCADE
    ColumnIDList = ListField(LazyReferenceField("Column"), default=list)  # , reverse_delete_rule=PULL
    SampleID = LazyReferenceField("Sample", null=True)  # , reverse_delete_rule=CASCADE
    ResearchItemID = LazyReferenceField("ResearchItem", null=True)  # , reverse_delete_rule=CASCADE
