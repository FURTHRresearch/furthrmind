from mongoengine import *
from .BaseClassProjectIDOptional import BaseClassProjectIDOptional


class ChemicalStructure(BaseClassProjectIDOptional):
    meta = {"collection": __qualname__}

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .FieldData import FieldData
        collection_attribute_list = [
            {"class": FieldData,
             "attr": FieldData.Value.name}
        ]
        ChemicalStructure.post_delete_nullify(collection_attribute_list, document.id)

    Smiles = StringField(default="")
    SmilesList = ListField(StringField(), default=[])
    MolfileString = StringField(default="")
    InChI = StringField(default="")
    InChIKey = StringField(default="")
    CDXML = StringField(default="")
