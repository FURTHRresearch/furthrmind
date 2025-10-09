from datetime import datetime, date

from mongoengine import *
from .BaseClassProjectIDOptional import BaseClassProjectIDOptional
from bson import ObjectId
from mongoengine.base.datastructures import LazyReference
import iteration_utilities

class Column(BaseClassProjectIDOptional):
    meta = {"collection": __qualname__,
            "indexes": [
                "UnitID"
            ]}

    @staticmethod
    def set_delete_rules():
        pass
        # from .Unit import Unit
        # direkt post delete method in Units
        # Unit.register_delete_rule(Column, "UnitID", NULLIFY)

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        from tenjin.mongo_engine import RawData
        if self._created:
            return
        raw_data = RawData.objects(ColumnIDList__in=[self.id]).first()
        if not raw_data:
            return
        if raw_data.ProjectID:
            self.ProjectID = raw_data.ProjectID


    @staticmethod
    def update_project_external_triggered(column_list, project):
        column = column_list[0]
        if isinstance(column, LazyReference):
            column_id_list = [c.id for c in column_list]
            column_list = Column.objects(id__in=column_id_list)
        elif isinstance(column, ObjectId):
            column_id_list = column_list
            column_list = Column.objects(id__in=column_id_list)

        for column in column_list:
            if column.ProjectID is not None:
                return
            column.ProjectID = project
            column.save(signal_kwargs={
                "Opr": "Update",
                "Attr": Column.ProjectID,
                "Value": project
            })

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .RawData import RawData
        from .Table import Table

        collection_attribute_list = [
            {"class": RawData,
             "attr": RawData.ColumnIDList.name},
            {"class": Table,
             "attr": Table.ColumnIDList.name}
        ]
        Column.post_delete_pull(collection_attribute_list, document.id)

    def clean(self):
        super().clean()
        self.check_values()

    def check_values(self):
        if self.Type == "Text":
            if not iteration_utilities.all_isinstance(self.Data, (str, type(None))):
                self.Data = list(map(self.convert_to_str, self.Data))
        elif self.Type == "Numeric":
            if not iteration_utilities.all_isinstance(self.Data, (float, type(None))):
                self.Data = list(map(self.convert_to_float, self.Data))
        elif self.Type == "Date":
            if not iteration_utilities.all_isinstance(self.Data, (datetime, type(None))):
                self.Data = list(map(self.convert_to_datetime, self.Data))
        elif self.Type == "Bool":
            if not iteration_utilities.all_isinstance(self.Data, (bool, type(None))):
                self.Data = list(map(self.convert_to_bool, self.Data))

    def convert_to_str(self, value):
        if not value:
            return None
        return str(value)

    def convert_to_float(self, value):
        if value is None:
            return None
        try:
            float_value = float(value)
            return float_value
        except ValueError:
            raise ValidationError(f"Value: {value} is not a numeric value. column: {self.id}, {self.Name}",
                                  errors={"Value": {"Value": value,
                                                    "List": True,
                                                    "Message": f"Value: {value} is not a numeric value. column: "
                                                               f"{self.id}, {self.Name}"}})

    def convert_to_bool(self, value):
        if not value:
            return None
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            if value.lower() in ("true", "yes", "1"):
                return True
            if value.lower() in ("false", "no", "0"):
                return False
        if isinstance(value, int):
            if value == 1:
                return True
            if value == 0:
                return False

        raise ValidationError(f"Value: {value} is not a boolean value. column: {self.id}, {self.Name}",
                              errors={"Value": {"Value": value,
                                                "List": True,
                                                "Message": f"Value: {value} is not a boolean value. column: "
                                                           f"{self.id}, {self.Name}"}})

    def convert_to_datetime(self, value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            value = datetime.combine(value, datetime.min.time())
            return value
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
                return value
            except ValueError:
                pass
        try:
            value = int(value)
            value = datetime.fromtimestamp(value)
            return value
        except ValueError:
            raise ValidationError(f"Value: {value} is not a valid datetime object, isoformat, or unix timestamp. column: {self.id}, {self.Name}",
                                  errors={"Value": {"Value": value,
                                                    "List": True,
                                                    "Message": f"Value: {value} is not a valid datetime object, isoformat, or unix timestamp. column: "
                                                               f"{self.id}, {self.Name}"}})

    Name = StringField(required=True)
    Type = StringField(required=True,
                       choices=("Text", "Numeric", "Date", "Bool"))
    UnitID = LazyReferenceField("Unit", null=True)  # , reverse_delete_rule=NULLIFY)
    Data = DynamicField(default=list)
    Default = DynamicField(null=True)

