import datetime

import flask
from bson import ObjectId
from mongoengine import *

from .BaseClassProjectID import BaseClassProjectID
from mongoengine.base import LazyReference


class FieldData(BaseClassProjectID):
    meta = {
        "collection": __qualname__,
        "indexes": [
            {"fields": ("FieldID", "ValueLower"), "name": "field_valuelower"},
            {"fields": ("FieldID", "Value"), "name": "field_value"},
            {"fields": ("FieldID", "SIValue"), "name": "field_sivalue"},
        ],
    }

    def __setattr__(self, key, value):
        prohibited_keys = ["FieldID", "Type"]
        permitted = self.check_prohibited_attributes(key, prohibited_keys)
        if permitted:
            super().__setattr__(key, value)

    @classmethod
    def post_init_method(cls, sender, document, **kwargs):
        super().post_init_method(sender, document, **kwargs)
        if document._created:
            document.update_field_type()
            document.update_si_value()
            document.update_si_value_max()
            document.update_author()
            document.update_notebook()
            document.update_value_lower()

    def update_project(self):
        super().update_project()
        if self.ProjectID is not None:
            return self.ProjectID
        field = self.FieldID.fetch()
        self.ProjectID = field.ProjectID

    def update_field_type(self):
        if self.Type is not None:
            return
        field = self.FieldID.fetch()
        self.Type = field.Type

    def update_value_lower(self):
        if isinstance(self.Value, str):
            self.ValueLower_old = self.ValueLower
            self.ValueLower = self.Value.lower()
            if self._created:
                return

            if self.ValueLower_old != self.ValueLower:
                self.save(
                    signal_kwargs={
                        "Opr": "Update",
                        "Attr": FieldData.ValueLower.name,
                        "Value": self.ValueLower,
                    }
                )
                self.update_fielddata_value_in_parent(
                    FieldData.ValueLower.name, self.ValueLower
                )

    def update_si_value(self):
        if self.Type in ["Numeric", "NumericRange"]:
            changed = False
            if self.Value:
                value = None
                try:
                    value = float(self.Value)
                except:
                    if self.SIValue is not None:
                        changed = True
                        self.SIValue = None
                if value:
                    if self.UnitID is None:
                        if self.SIValue != value:
                            changed = True
                            self.SIValue = value
                    else:
                        try:
                            unit = self.UnitID.fetch()
                            check, si_value = unit.unit_conversion_to_si(value)
                            if not check:
                                if self.SIValue != value:
                                    changed = True
                                    self.SIValue = value
                            else:
                                if self.SIValue != si_value:
                                    changed = True
                                    self.SIValue = si_value
                        except:
                            if self.SIValue != value:
                                changed = True
                                self.SIValue = value

            else:
                if self.SIValue is not None:
                    changed = True
                    self.SIValue = None
            if not self._created and changed:
                self.save(
                    signal_kwargs={
                        "Opr": "Update",
                        "Attr": FieldData.SIValue.name,
                        "Value": self.SIValue,
                    }
                )
                self.update_fielddata_value_in_parent(
                    FieldData.SIValue.name, self.SIValue
                )

    def update_si_value_max(self):
        if self.Type in ["Numeric", "NumericRange"]:
            changed = False
            if self.ValueMax:
                value = None
                try:
                    value = float(self.ValueMax)
                except:
                    if self.SIValueMax is not None:
                        changed = True
                        self.SIValueMax = None
                if value:
                    if self.UnitID is None:
                        if self.SIValueMax != value:
                            changed = True
                            self.SIValueMax = value
                    else:
                        try:
                            unit = self.UnitID.fetch()
                            check, si_value = unit.unit_conversion_to_si(value)
                            if not check:
                                if self.SIValueMax != value:
                                    changed = True
                                    self.SIValueMax = value
                            else:
                                if self.SIValueMax != si_value:
                                    changed = True
                                    self.SIValueMax = si_value
                        except:
                            if self.SIValueMax != value:
                                changed = True
                                self.SIValueMax = value

            else:
                if self.SIValueMax is not None:
                    changed = True
                    self.SIValueMax = None
            if not self._created and changed:
                self.save(
                    signal_kwargs={
                        "Opr": "Update",
                        "Attr": FieldData.SIValueMax.name,
                        "Value": self.SIValueMax,
                    }
                )
                self.update_fielddata_value_in_parent(
                    FieldData.SIValueMax.name, self.SIValueMax
                )

    def update_author(self):
        if self.AuthorID is not None:
            return
        from .Author import Author
        if hasattr(flask.g, "user"):
            user_id = flask.g.user
            a = Author.objects(UserID=user_id)[0]
            self.AuthorID = a.id

    def update_notebook(self):
        from tenjin.execution.create import Create

        if self.Type == "MultiLine" and self.Value is None:
            data = {
                "Content": "",
                "FileIDList": [],
                "ImageFileIDList": [],
                "ProjectID": self.ProjectID.id,
            }
            notebook_id = Create.create("Notebook", data)
            self.Value = notebook_id

    def set_calculation(self, calculation_id):
        self.Value = calculation_id
        self.save(
            signal_kwargs={
                "Opr": "Update",
                "Attr": FieldData.Value.name,
                "Value": calculation_id,
            }
        )
        self.update_fielddata_value_in_parent(
                    FieldData.Value.name, calculation_id
                )

    def update_chemical_structure_project(self):
        from tenjin.execution.update import Update

        if self.Type == "ChemicalStructure" and self.Value is not None:
            chem_id = self.Value.id
            Update.update("ChemicalStructure", "ProjectID", self.ProjectID, chem_id)

    def update_notebook_project(self):
        from tenjin.execution.update import Update

        if self.Type == "MultiLine" and self.Value is not None:
            notebook_id = self.Value.id
            Update.update("Notebook", "ProjectID", self.ProjectID, notebook_id)

    def update_values_from_range(self):
        if not self.Type == "NumericRange":
            return
        if not self.InternalValueNumericRange:
            return

        from tenjin.execution.update import Update

        value = self.InternalValueNumericRange[0]
        value_max = self.InternalValueNumericRange[1]
        if value and value_max:
            if value > value_max:
                value, value_max = value_max, value
        Update.update("FieldData", "Value", value, self.id)
        Update.update("FieldData", "ValueMax", value_max, self.id)

    def create_method(self, kwargs):
        self.update_values_from_range()

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return

        if attr == FieldData.Value.name:
            self.update_si_value()
            self.update_value_lower()
            self.update_chemical_structure_project()
            
            self.update_fielddata_value_in_parent(
                    FieldData.Value.name, self.Value
                )

        elif attr == FieldData.ValueMax.name:
            self.update_si_value_max()
            self.update_fielddata_value_in_parent(
                    FieldData.ValueMax.name, self.ValueMax
                )

        elif attr == FieldData.UnitID.name:
            self.update_si_value()
            self.update_si_value_max()

        elif attr == FieldData.InternalValueNumericRange.name:
            self.update_values_from_range()

    def clean(self):
        super().clean()
        self.check_value()

    def check_value(self):
        value = self.Value
        if value is None:
            return
        field_type = self.Type
        if field_type in ["Numeric", "NumericRange"]:
            try:
                self.Value = float(value)
            except:
                raise ValidationError(
                    f"Value: {value} is not a numeric value. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a numeric value. Field: {self.FieldID}",
                        }
                    },
                )

            if self.ValueMax:
                try:
                    self.ValueMax = float(self.ValueMax)
                except:
                    raise ValidationError(
                        f"ValueMax: {self.ValueMax} is not a numeric value. Field: {self.FieldID}",
                        errors={
                            "Value": {
                                "Value": self.ValueMax,
                                "List": False,
                                "Message": f"Value: {self.ValueMax} is not a numeric value. Field: {self.FieldID}",
                            }
                        },
                    )

        elif field_type == "Date":
            if isinstance(value, (int, float)):
                value = float(value)
                try:
                    self.Value = datetime.datetime.fromtimestamp(value)
                except:
                    raise ValidationError(
                        f"Value: {value} is not a valid datetime format. Field: {self.FieldID}",
                        errors={
                            "Value": {
                                "Value": self.Value,
                                "List": False,
                                "Message": f"Value: {value} is not a valid datetime format. Field: {self.FieldID}",
                            }
                        },
                    )
            elif isinstance(value, datetime.datetime):
                pass
            elif isinstance(value, str):
                try:
                    self.Value = datetime.fromisoformat(value)
                except:
                    raise ValidationError(
                        f"Value: {value} is not a valid datetime format. Field: {self.FieldID}",
                        errors={
                            "Value": {
                                "Value": self.Value,
                                "List": False,
                                "Message": f"Value: {value} is not a valid datetime format. Field: {self.FieldID}",
                            }
                        },
                    )

            else:
                raise ValidationError(
                    f"Value: {value} is not a valid datetime format. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a valid datetime format. Field: {self.FieldID}",
                        }
                    },
                )

        elif field_type in ["ComboBox", "ComboBoxSynonym"]:
            from .ComboBoxEntry import ComboBoxEntry

            combobox = None
            if isinstance(value, (LazyReferenceField, ComboBoxEntry)):
                combobox = ComboBoxEntry.objects(id=value.id)
            elif isinstance(value, ObjectId):
                combobox = ComboBoxEntry.objects(id=value)
            if not combobox:
                raise ValidationError(
                    f"Value: {value} is not a valid combobox. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a valid combobox. Field: {self.FieldID}",
                        }
                    },
                )

        elif field_type in ["SingleLine"]:
            if type(value) is not str:
                self.Value = str(value)

        elif field_type == "MultiLine":
            from .Notebook import Notebook

            notebook = None
            if isinstance(value, (LazyReferenceField, Notebook)):
                notebook = Notebook.objects(id=value.id)
            elif isinstance(value, ObjectId):
                notebook = Notebook.objects(id=value)
            if not notebook:
                raise ValidationError(
                    f"Value: {value} is not a valid notebook. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a valid notebook. Field: {self.FieldID}",
                        }
                    },
                )

        elif field_type == "CheckBox":
            if type(value) is str:
                if value.lower() == "true":
                    self.Value = True
                elif value.lower() == "false":
                    self.Value = False
                else:
                    raise ValidationError(
                        f"Value: {value} is not a valid checkbox format. Field: {self.FieldID}",
                        errors={
                            "Value": {
                                "Value": self.Value,
                                "List": False,
                                "Message": f"Value: {value} is not a valid checkbox format. Field: {self.FieldID}",
                            }
                        },
                    )
            elif type(value) is not bool:
                raise ValidationError(
                    f"Value: {value} is not a valid checkbox format. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a valid checkbox format. Field: {self.FieldID}",
                        }
                    },
                )

        elif field_type in ["RawDataCalc", "Calculation"]:
            from .Calculation import Calculation

            calc = None
            if isinstance(value, (LazyReferenceField, Calculation)):
                calc = Calculation.objects(id=value.id)
            elif isinstance(value, ObjectId):
                calc = Calculation.objects(id=value)
            if not calc:
                raise ValidationError(
                    f"Value: {value} is not a valid calculation. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a valid calculation. Field: {self.FieldID}",
                        }
                    },
                )

        elif field_type == "Table":
            from .Table import Table

            table = None
            if isinstance(value, (LazyReferenceField, Table)):
                table = Table.objects(id=value.id)
            elif isinstance(value, ObjectId):
                table = Table.objects(id=value)
            if not table:
                raise ValidationError(
                    f"Value: {value} is not a valid table. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a valid table. Field: {self.FieldID}",
                        }
                    },
                )

        elif field_type == "ChemicalStructure":
            from .ChemicalStructure import ChemicalStructure

            chem = None
            if isinstance(value, (LazyReferenceField, ChemicalStructure)):
                chem = ChemicalStructure.objects(id=value.id)
            elif isinstance(value, ObjectId):
                chem = ChemicalStructure.objects(id=value)
            if not chem:
                raise ValidationError(
                    f"Value: {value} is not a valid chemical structure. Field: {self.FieldID}",
                    errors={
                        "Value": {
                            "Value": self.Value,
                            "List": False,
                            "Message": f"Value: {value} is not a valid chemical structure. Field: {self.FieldID}",
                        }
                    },
                )

        else:
            raise ValidationError(
                "Not a valid field type",
                errors={
                    "Value": {
                        "Value": self.Value,
                        "List": False,
                        "Message": "Not a valid field type",
                    }
                },
            )
        # todo missing field_types: Link, User, File

        if self.InternalValueNumericRange is not None:
            if not isinstance(self.InternalValueNumericRange, list):
                raise ValidationError(
                    "Numeric range value must be a list",
                    errors={
                        "Value": {
                            "Value": self.InternalValueNumericRange,
                            "List": True,
                            "Message": "Numeric range value must be a list",
                        }
                    },
                )
            if not len(self.InternalValueNumericRange) == 2:
                raise ValidationError(
                    "Numeric range value must be a list with 2 elements",
                    errors={
                        "Value": {
                            "Value": self.InternalValueNumericRange,
                            "List": True,
                            "Message": "Numeric range value must be a list with 2 elements",
                        }
                    },
                )

            value = self.InternalValueNumericRange[0]
            value_max = self.InternalValueNumericRange[1]
            if value == "":
                value = None
                self.InternalValueNumericRange[0] = value
            if value_max == "":
                value_max = None
                self.InternalValueNumericRange[1] = value_max

    def set_value_to_none(self):
        from tenjin.execution.update import Update

        Update.update("FieldData", "Value", None, self.id)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from tenjin.execution.pop import Pop
        
        parent_collection = document.ParentCollection
        parent_id = document.ParentDataID
        if parent_collection and parent_id:
            Pop.pop(parent_collection, "FieldDataIDList", parent_id, document.id)

        from .Calculation import Calculation

        collection_attribute_list = [
            {"class": Calculation, "attr": Calculation.FieldDataID.name},
        ]
        FieldData.post_delete_cascade(collection_attribute_list, document.id)

    @classmethod
    def add_parent_collection_and_id(cls, parent_collection, parent_id):
        from tenjin.execution.update import Update

        Update.update("FieldData", "ParentCollection", parent_collection, parent_id)
        Update.update("FieldData", "ParentDataID", parent_id, parent_id)

    def update_fielddata_value_in_parent(self, attribute, value):
        if self.ParentCollection is None or self.ParentDataID is None:
            return
        from tenjin.mongo_engine import Database
        from tenjin.execution.update import Update

        assert attribute in ["Value", "ValueMax", "SIValue", "SIValueMax", "ValueLower"]
        parent_cls, parent_doc = Database.get_collection_class_and_document(
            self.ParentCollection, self.ParentDataID, only=("id", "FieldData", "ProjectID")
        )
        for fd in parent_doc.FieldData:
            if fd._id == self.id:
                fd[attribute] = value
                signal_kwargs = {"NoVersioning": True}
                parent_doc.save(validate=False, signal_kwargs=signal_kwargs)
                break
        pass

    @classmethod
    def update_fielddata_in_parent(
        cls,
        parent_collection,
        parent_id,
    ):
        from tenjin.execution.update import Update
        from tenjin.execution.delete import Delete
        from tenjin.mongo_engine import Database
        from tenjin.mongo_engine.FieldDataEmbedded import FieldDataEmbedded

        parentcls, parent_doc = Database.get_collection_class_and_document(
            parent_collection,
            parent_id,
            only=("id", "FieldDataIDList", "FieldData", "ProjectID"),
        )
        fielddata_ids = [fd.id for fd in parent_doc.FieldDataIDList]
        fielddata = FieldData.objects(id__in=fielddata_ids)
        old_fd_ids = [fd._id for fd in parent_doc.FieldData]
        fd_to_be_deleted = []
        for old_fd_id in old_fd_ids:
            if old_fd_id not in fielddata_ids:
                fd_to_be_deleted.append(old_fd_id)
                
        fielddata_mapping = {fd.id: fd for fd in fielddata}
        fielddata_embedded_list = []
        for fd_id in fielddata_ids:
            if fd_id not in fielddata_mapping:
                raise ValidationError(
                    "FieldData not found",
                    errors={
                        "FieldData": {
                            "Value": fd_id,
                            "List": False,
                            "Message": "FieldData not found",
                        }
                    },
                )
            fd = fielddata_mapping[fd_id]
            data = {
                "_id": fd.id,
                "FieldID": fd.FieldID.id,
                "Type": fd.Type,
                "Value": fd.Value,
                "SIValue": fd.SIValue,
                "ValueMax": fd.ValueMax,
                "ValueLower": fd.ValueLower,
                "SIValueMax": fd.SIValueMax,
            }
            fielddata_embedded = FieldDataEmbedded(**data)
            fielddata_embedded_list.append(fielddata_embedded)
            if not fd.ParentCollection == parent_collection:
                Update.update("FieldData", "ParentCollection", parent_collection, fd.id)
            if not fd.ParentDataID == parent_id:
                Update.update("FieldData", "ParentDataID", parent_id, fd.id)

        Update.update(parent_collection, "FieldData", fielddata_embedded_list, parent_id)
        for fd_id in fd_to_be_deleted:
            if FieldData.objects(id=fd_id).first():
                # To avoid a loop, remove parent collection and id before deleting
                Update.update("FieldData", "ParentCollection", None, fd_id, no_versioning=True)
                Update.update("FieldData", "ParentDataID", None, fd_id, no_versioning=True)
                Delete.delete("FieldData", fd_id)

    @classmethod
    def append_fielddata_to_parent(cls, parent_collection, parent_id, fielddata_id):
        from tenjin.execution.append import Append
        from tenjin.execution.update import Update
        from tenjin.mongo_engine.FieldDataEmbedded import FieldDataEmbedded

        doc = FieldData.objects(id=fielddata_id).first()
        if doc is None:
            raise ValidationError(
                f"FieldData not found: {fielddata_id}",
                errors={
                    "FieldData": {
                        "Value": fielddata_id,
                        "List": False,
                        "Message": f"FieldData not found: {fielddata_id}",
                    }
                },
            )
        data = {
            "_id": doc.id,
            "FieldID": doc.FieldID.id,
            "Type": doc.Type,
            "Value": doc.Value,
            "SIValue": doc.SIValue,
            "ValueMax": doc.ValueMax,
            "ValueLower": doc.ValueLower,
            "SIValueMax": doc.SIValueMax,
        }
        if isinstance(data["Value"], LazyReference):
            data["Value"] = data["Value"].id

        fielddata_embedded = FieldDataEmbedded(**data)
        Append.append(
            parent_collection, "FieldData", parent_id, fielddata_embedded, no_versioning=True
        )
        Update.update("FieldData", "ParentCollection", parent_collection, fielddata_id)
        Update.update("FieldData", "ParentDataID", parent_id, fielddata_id)

    @classmethod
    def remove_fielddata_from_parent(cls, parent_collection, parent_id, fielddata_id):
        from tenjin.mongo_engine import Database
        from tenjin.execution.pop import Pop
        from tenjin.execution.update import Update
        from tenjin.execution.delete import Delete

        parent_cls, parent_doc = Database.get_collection_class_and_document(
            parent_collection, parent_id, only=("id", "FieldData", "ProjectID")
        )

        if not parent_doc:
            raise ValidationError(
                f"Parent not found: {parent_id}",
                errors={
                    "Parent": {
                        "Value": parent_id,
                        "List": False,
                        "Message": f"Parent not found: {parent_id}",
                    }
                },
            )

        item_to_be_removed = None
        for item in parent_doc.FieldData:
            if item._id == fielddata_id:
                item_to_be_removed = item
                break
        if item_to_be_removed is None:
            raise ValidationError(
                f"FieldData not found: {fielddata_id}",
                errors={
                    "FieldData": {
                        "Value": fielddata_id,
                        "List": False,
                        "Message": f"FieldData not found in parent: {fielddata_id}",
                    }
                },
            )
        Pop.pop(
            parent_collection,
            "FieldData",
            parent_id,
            item_to_be_removed,
            no_versioning=True,
        )
        # if fielddata not deleted, remove parent collection and id
        if FieldData.objects(id=fielddata_id).only("id").first():
            # To avoid a loop, remove parent collection and id before deleting
            Update.update("FieldData", "ParentCollection", None, fielddata_id, no_versioning=True)
            Update.update("FieldData", "ParentDataID", None, fielddata_id, no_versioning=True)
            Delete.delete("FieldData", fielddata_id)

        

    FieldID = LazyReferenceField(
        "Field", required=True
    )  # , reverse_delete_rule=CASCADE)
    Type = StringField(
        required=True,
        choices=(
            "Numeric",
            "NumericRange",
            "Date",
            "ComboBox",
            "ComboBoxSynonym",
            "SingleLine",
            "MultiLine",
            "CheckBox",
            "RawDataCalc",
            "Link",
            "User",
            "File",
            "Table",
            "ChemicalStructure",
            "Calculation",
        ),
    )
    Value = DynamicField(null=True)
    UnitID = LazyReferenceField("Unit", null=True)  # , reverse_delete_rule=NULLIFY)
    SIValue = FloatField(null=True)
    AuthorID = LazyReferenceField("Author", null=True)  # , reverse_delete_rule=NULLIFY)
    ValueMax = FloatField(null=True)
    ValueLower = StringField(null=True)
    SIValueMax = FloatField(null=True)
    InternalValueNumericRange = ListField(null=True)
    ParentCollection = StringField(
        null=True,
        choices=(
            "Experiment",
            "Sample",
            "Group",
            "ResearchItem",
            "ComboBoxEntry",
        ),
    )
    ParentDataID = ObjectIdField(null=True)
