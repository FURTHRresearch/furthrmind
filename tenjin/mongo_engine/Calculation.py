from mongoengine import *
from .BaseClassProjectID import BaseClassProjectID

class Calculation(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "FieldDataID"
            ]}

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        field_data = self.FieldDataID.fetch()
        self.ProjectID = field_data.ProjectID

    def create_method(self, kwargs):
        for attr in [Calculation.FieldDataID]:
            self.update_method({"Attr": attr})

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == Calculation.FieldDataID.name:
            field_data = self.FieldDataID
            field_data = field_data.fetch()
            field_data.set_calculation(self.id)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .FieldData import FieldData
        collection_attribute_list = [
            {"class": FieldData,
             "attr": FieldData.Value.name}
        ]
        Calculation.post_delete_nullify(collection_attribute_list, document.id)

    FieldDataID = LazyReferenceField("FieldData", required=True)#, reverse_delete_rule=CASCADE)
    Output = DictField(default=dict)
    LastExecution = DateTimeField(null=True)
    UpToDate = BooleanField(null=True)
    TriggerIDList = ListField(LazyReferenceField("Trigger"), default=list)
