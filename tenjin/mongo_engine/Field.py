from mongoengine import *

from .BaseClassProjectID import BaseClassProjectID


class Field(BaseClassProjectID):
    meta = {"collection": __qualname__,
            "indexes": [
                "ComboBoxFieldID",
                "ProjectID",
                ("ProjectID", "NameLower")
            ]}

    def __setattr__(self, key, value):
        prohibited_keys = ["Type"]
        permitted = self.check_prohibited_attributes(key, prohibited_keys)
        if permitted:
            super().__setattr__(key, value)

    def clean(self):
        super().clean()
        count = Field.objects(NameLower=self.NameLower, ProjectID=self.ProjectID, id__ne=self.id).count()
        if count > 0:
            raise ValidationError("Field name must be unique within this project",
                                  errors={"Name": {"Value": self.Name,
                                                   "List": False,
                                                   "Message": "Field name must be unique within this project"}})

    @staticmethod
    def validate_combo_and_combosynonym(field):
        if field is None:
            return
        field = field.fetch()
        if field.Type != "ComboBox":
            raise ValidationError("This is not a valid combobox field",
                                  errors={"Type": {"Value": field.Type,
                                                   "List": False,
                                                   "Message": "This field is not a ComboBox"}})

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        if flag in ["write", "delete"]:
            # only project admins can create, delete or modify fields
            flag = "invite"
        return super().check_permission(document_list, flag, user, signal_kwargs)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .ComboBoxEntry import ComboBoxEntry
        from .FieldData import FieldData

        collection_attribute_list = [
            {"class": ComboBoxEntry,
             "attr": ComboBoxEntry.FieldID.name},
            {"class": FieldData,
             "attr": FieldData.FieldID.name},
        ]
        Field.post_delete_cascade(collection_attribute_list, document.id)

    Type = StringField(required=True,
                       choices=("Numeric", "Date", "ComboBox",
                                "ComboBoxSynonym", "SingleLine",
                                "MultiLine", "CheckBox", "RawDataCalc",
                                "NumericRange",
                                "Link", 
                                # "User", "File", "Table",
                                "ChemicalStructure"))
    ComboBoxFieldID = LazyReferenceField("self", null=True, validation=validate_combo_and_combosynonym)
    #  reverse_delete_rule=CASCADE)
    Name = StringField(required=True)
    NameLower = StringField(required=True)
    RawDataCalcOutputList = ListField(StringField(), default=list)
    RawDataCalcScriptFileID = LazyReferenceField("File", null=True)  # , reverse_delete_rule=NULLIFY)
    WebDataCalcScript = StringField(null=True)
    CalculationType = StringField(null=True, choices=("WebDataCalc", "Spreadsheet", "Wrapper"))
