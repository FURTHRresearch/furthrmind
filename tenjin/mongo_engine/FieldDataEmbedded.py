from mongoengine import *
from bson import ObjectId

class FieldDataEmbedded(EmbeddedDocument):
    _id = ObjectIdField(default=ObjectId)
    FieldID = LazyReferenceField("Field", required=True)  # , reverse_delete_rule=CASCADE)
    Type = StringField(required=True,
                       choices=("Numeric", "NumericRange", "Date", "ComboBox",
                                "ComboBoxSynonym", "SingleLine",
                                "MultiLine", "CheckBox", "RawDataCalc",
                                "Link", "User", "File", "Table",
                                "ChemicalStructure", "Calculation"))
    Value = DynamicField(null=True)
    SIValue = FloatField(null=True)
    ValueMax = FloatField(null=True)
    ValueLower = StringField(null=True)
    SIValueMax = FloatField(null=True)
