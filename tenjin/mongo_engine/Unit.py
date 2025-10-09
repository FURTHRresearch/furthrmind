from mongoengine import *
from .BaseClassProjectIDOptional import BaseClassProjectIDOptional
from bson import ObjectId
import numericalunits as nu
from tenjin.tasks.rq_task import create_task


class Unit(BaseClassProjectIDOptional):
    meta = {"collection": __qualname__, "indexes": ["ProjectID", "Predefined"]}

    def clean(self):
        super().clean()

        units = Unit.objects(
            (Q(Predefined=True) | Q(ProjectID=self.ProjectID))
            & Q(ShortName=self.ShortName)
        )
        if len(units) > 0:
            if len(units) == 1 and units[0].id == self.id:
                return
            raise ValidationError(
                "ShortName cannot be equal to predefined unit or with another unit from the same project",
                errors={
                    "ShortName": {
                        "Value": self.ShortName,
                        "List": False,
                        "Message": "ShortName cannot be equal to predefined unit or with another unit from the same project",
                    }
                },
            )

    def update_method(self, kwargs):
        attr = kwargs.get("Attr")
        if not attr:
            return
        if attr == "Definition":
            create_task(Unit.update_si_value_all_fieddata, self.id, job_timeout=86400)

    @staticmethod
    def update_si_value_all_fieddata(unit_id):
        from .FieldData import FieldData
        field_data = FieldData.objects(UnitID=unit_id)
        for fd in field_data:
            fd.update_si_value()

    def unit_conversion_to_si(self, value):
        try:
            if value is None:
                return True, value

            definition = self.Definition
            if "<u>" in definition:  # Self-defined
                while definition.find("<u>") != -1:
                    startFirstIdentifier = definition.find("<u>")
                    endFirstIdentifier = startFirstIdentifier + 3
                    startSecondIdentifier = definition.find("</u>")
                    endSecondIdentifier = startSecondIdentifier + 4

                    newUnitID = definition[endFirstIdentifier:startSecondIdentifier]
                    newUnitID = newUnitID.replace(" ", "")
                    newUnitID = ObjectId(newUnitID)
                    new_unit = Unit.objects(id=newUnitID).first()
                    if new_unit is None:
                        return False, None
                    check, result = new_unit.unit_conversion_to_si(1)
                    if not check:
                        return check, result
                    definition = definition.replace(
                        definition[startFirstIdentifier:endSecondIdentifier],
                        str(result),
                    )
                try:
                    factor = eval(definition)
                except:
                    factor = 1
                value = float(value) * factor
                return True, value
            else:
                if definition == "degC":
                    value = float(value) + 273.15
                elif "mol" in definition:
                    nu.reset_units("SI")
                    try:
                        factor = eval("nu.{} / nu.mol".format(definition))
                    except:
                        factor = 1
                    value = float(value) * factor
                else:
                    nu.reset_units("SI")
                    try:
                        factor = eval("nu." + definition)
                    except:
                        return False, None
                    value = float(value) * factor
                return True, value
        except Exception as e:
            return False, None

    @classmethod
    def check_permission(cls, document_list, flag, user=None, signal_kwargs=None):
        if flag in ["write", "delete"]:
            # only project admins can create, delete or modify fields
            flag = "invite"
        return super().check_permission(document_list, flag, user, signal_kwargs)

    @classmethod
    def post_delete_method(cls, sender, document, **kwargs):
        super().post_delete_method(sender, document, **kwargs)
        from .Column import Column
        from .FieldData import FieldData

        collection_attribute_list = [
            {"class": Column, "attr": "UnitID"},
            {"class": FieldData, "attr": "UnitID"},
        ]
        Unit.post_delete_nullify(collection_attribute_list, document.id)

    @classmethod
    def pre_save_method(cls, sender, document: Document, **kwargs):
        super().pre_save_method(sender, document, **kwargs)

    
        attribute = kwargs.get("Attr", None)
        operation = kwargs.get("Opr", None)
        if attribute == "Definition" and operation == "Update":
            # if definition is updated check if definition must be replaced with correct definition string
            cls.update_definition(document)
        if operation == "Create":
            cls.update_definition(document)

    @classmethod
    def update_definition(cls, doc):
        definition = doc.Definition
        if definition is None:
            return
        # only update if <u> is not in the definition. This means, def was already correctly updated
        if "<u>" in definition:
            return
        from tenjin.database.db import get_db

        db = get_db().db
        sorted_units = list(
            db["Unit"].aggregate(
                [
                    {
                        "$match": {
                            "$or": [
                                {"Predefined": True},
                            ]
                        }
                    },
                    {
                        "$project": {
                            "length": {"$strLenCP": "$ShortName"},
                            "ShortName": 1,
                        }
                    },
                    {"$sort": {"length": -1}},
                ]
            )
        )
        for unit in sorted_units:
            if unit["ShortName"] in definition:
                definition = definition.replace(unit["ShortName"], f"<u>{unit['_id']}</u>")
        doc.Definition = definition
        
    Definition = StringField(null=True)
    LongName = StringField(null=True)
    Predefined = BooleanField(default=False)
    ShortName = StringField(required=True)
    UnitCategoryIDList = ListField(
        LazyReferenceField("UnitCategory"), default=list
    )  # , reverse_delete_rule=PULL
