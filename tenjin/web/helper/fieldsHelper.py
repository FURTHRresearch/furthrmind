import datetime

import bson
import flask
from tenjin.database.db import get_db
from tenjin.execution.create import Create
from tenjin.mongo_engine.ResearchCategory import ResearchCategory
from tenjin.mongo_engine.FieldData import FieldData

from .furthrHelper import append


def getFields(FieldDataIdList, table=False):

    db = get_db().db
    fieldData = [
        {
            "FieldID": str(f["FieldID"]),
            "id": str(f["_id"]),
            "Value": (
                str(f["Value"])
                if (type(f["Value"]) == bson.objectid.ObjectId)
                else f["Value"]
            ),
            "UnitID": str(f["UnitID"]),
            "OwnerID": str(f["OwnerID"]),
            "AuthorID": str(f["AuthorID"]),
            "SIValue": f["SIValue"],
            "ValueMax": f["ValueMax"],
            "SIValueMax": f["SIValueMax"],
        }
        for f in db.FieldData.find({"_id": {"$in": FieldDataIdList}})
    ]

    fieldIds = [bson.ObjectId(f["FieldID"]) for f in fieldData]
    fields = {
        str(f["_id"]): {
            "Type": f["Type"],
            "Name": f["Name"],
            "ComboBoxFieldID": f["ComboBoxFieldID"],
            "calculationType": f["CalculationType"],
        }
        for f in db.Field.find({"_id": {"$in": fieldIds}})
    }

    for f in fieldData:
        if f["FieldID"] not in fields:
            continue
        f["calculationType"] = fields[f["FieldID"]]["calculationType"]
        f["Type"] = fields[f["FieldID"]]["Type"]
        f["Name"] = fields[f["FieldID"]]["Name"]

        if f["Type"] == "RawDataCalc":
            res = db["Calculation"].find_one({"FieldDataID": bson.ObjectId(f["id"])})
            if not res:
                f["calculationResult"] = None
                continue
            value = {}
            if isinstance(res["Output"], dict):
                
                for key in res["Output"]:
                    v = res["Output"][key]
                    if isinstance(v, dict):
                        value[key] = str(v)
                    else:
                        value[key] = v
                
            else:
                value = str(res["Output"])
            f["calculationResult"] = value
            
        elif f["Type"] == "ComboBoxSynonym":
            f["FieldID"] = str(fields[f["FieldID"]]["ComboBoxFieldID"])
        elif f["Type"] == "MultiLine":
            if f["Value"]:
                notebook = db.Notebook.find_one({"_id": bson.ObjectId(f["Value"])})
                teaser = (
                    notebook["Content"][:100]
                    if notebook and notebook["Content"]
                    else ""
                )
                f["Teaser"] = (
                    teaser + "..." if len(teaser) > 100 or teaser == "" else teaser
                )
            else:
                f["Value"] = "..."
        elif f["Type"] == "ChemicalStructure":
            if f["Value"]:
                structure = db.ChemicalStructure.find_one(
                    {"_id": bson.ObjectId(f["Value"])}
                )
                smiles = ""
                cdxml = ""
                if structure.get("Smiles"):
                    smiles = structure.get("Smiles")
                if structure.get("CDXML"):
                    cdxml = structure.get("CDXML")
                f["smiles"] = smiles
                f["cdxml"] = cdxml
        elif f["Type"] == "Date":
            if f["Value"] is None:
                f["Value"] = ""
            elif f["Value"]:
                value = f["Value"].isoformat()
                # remove ms
                if "." in value:
                    f["Value"] = value.split(".")[0]
                else:
                    f["Value"] = value
        elif f["Type"] == "NumericRange":
            f["Value"] = [f["Value"], f["ValueMax"]]

        if f["Type"] == "Numeric" and table:
            unitID = bson.ObjectId(f["UnitID"]) if f["UnitID"] != "None" else None
            unit = db["Unit"].find_one({"_id": unitID})["ShortName"] if unitID else ""
            f["Value"] = str(f["Value"]) + " " + unit

        if f["Type"] == "NumericRange" and table:
            unitID = bson.ObjectId(f["UnitID"]) if f["UnitID"] != "None" else None
            unit = db["Unit"].find_one({"_id": unitID})["ShortName"] if unitID else ""
            f["Value"] = f"{f['Value']} - {f['ValueMax']} {unit}"

    field_data_mapping = {f["id"]: f for f in fieldData}
    field_data_result = []
    for f_id in FieldDataIdList:
        f_id = str(f_id)
        if f_id not in field_data_mapping:
            continue
        field_data_result.append(field_data_mapping[f_id])
    return field_data_result


def get_field_data_values(field_data_id_list, field_id_list=None):
    from tenjin.mongo_engine.Field import Field

    if not field_id_list:
        field_data_list = list(
            get_db().db.FieldData.find(
                {"_id": {"$in": field_data_id_list}}
            )
        )
        field_id_list = list(set([f["FieldID"] for f in field_data_list]))
    else:
        field_data_list = list(
            get_db().db.FieldData.find(
                {"_id": {"$in": field_data_id_list}, "FieldID": {"$in": field_id_list}}
            )
        )
    fields = Field.objects(id__in=field_id_list)
    field_mapping = {f.id: f for f in fields}

    unit_mapping = {}
    unit_id_list = []

    calculation_id_list = []
    calculation_mapping = {}

    notebook_id_list = []
    notebook_mapping = {}

    combo_box_id_list = []
    combo_mapping = {}

    for field_data in field_data_list:
        value = field_data["Value"]
        unit_id = field_data.get("UnitID")
        if unit_id:
            unit_id_list.append(unit_id)

        if field_data["Type"] == "RawDataCalc":
            calculation_id_list.append(value)

        elif field_data["Type"] == "MultiLine":
            notebook_id_list.append(value)

        elif field_data["Type"] == "ComboBox":
            combo_box_id_list.append(value)

    if unit_id_list:
        units = get_db().db.Unit.find({"_id": {"$in": unit_id_list}})
        unit_mapping = {unit["_id"]: unit for unit in units}

    if calculation_id_list:
        calcs = get_db().db.Calculation.find({"_id": {"$in": calculation_id_list}})
        calculation_mapping = {calc["_id"]: calc for calc in calcs}

    if notebook_id_list:
        notebooks = get_db().db.Notebook.find({"_id": {"$in": notebook_id_list}})
        notebook_mapping = {notebook["_id"]: notebook for notebook in notebooks}

    if combo_box_id_list:
        combos = get_db().db.ComboBoxEntry.find({"_id": {"$in": combo_box_id_list}})
        combo_mapping = {combo["_id"]: combo for combo in combos}

    field_data_mapping = {}
    for field_data in field_data_list:

        si_value = field_data["SIValue"]
        si_value_max = field_data["SIValueMax"]
        value = field_data["Value"]
        value_max = field_data["ValueMax"]
        unit_id = field_data["UnitID"]
        if isinstance(value, (int, float)):
            original_value = value
        else:
            original_value = None
        if isinstance(value_max, (int, float)):
            original_value_max = value_max
        else:
            original_value_max = None
        field = field_mapping[field_data["FieldID"]]
        result_dict = {
            "field_id": str(field_data["FieldID"]),
            "field_name": field["Name"],
            "value": value,
            "original_value": original_value,
            "si_value": si_value,
            "si_value_max": si_value_max,
            "unit": None,
            "type": field["Type"],
        }

        if field["Type"] == "Numeric":
            if unit_id:
                value = f"{value} {unit_mapping[unit_id]['ShortName']}"
                unit = unit_mapping[unit_id]["ShortName"]
                result_dict["value"] = value
                result_dict["unit"] = unit
        elif field["Type"] == "NumericRange":
            if unit_id:
                value = f"{value} - {value_max} {unit_mapping[unit_id]['ShortName']}"
                unit = unit_mapping[unit_id]["ShortName"]
                original_value = [original_value, original_value_max]
                result_dict["value"] = value
                result_dict["unit"] = unit
                result_dict["original_value"] = original_value
            else:
                value = f"{value} - {value_max}"
                original_value = [original_value, original_value_max]
                result_dict["value"] = value
                result_dict["original_value"] = original_value
        elif field["Type"] == "RawDataCalc":
            calc_id = value
            if calc_id:
                value = calculation_mapping[calc_id]["Output"]
                result_dict["value"] = str(value)
                result_dict["original_value"] = value
        elif field["Type"] == "MultiLine":
            notebook_id = value
            if notebook_id:
                notebook_content = notebook_mapping[notebook_id]["Content"]
                if len(notebook_content) > 100:
                    result_dict["value"] = notebook_content[:100] + "..."
                else:
                    result_dict["value"] = notebook_content
        elif field["Type"] == "ComboBox":
            combo_box_id = value
            if combo_box_id:
                value = combo_mapping[combo_box_id]["Name"]
                result_dict["value"] = value
        elif field["Type"] == "Date":
            if value:
                value = value.isoformat()
                if "." in value:
                    value = value.split(".")[0]
            else:
                value = ""
            result_dict["value"] = value

        field_data_mapping[field_data["_id"]] = result_dict

    return field_data_mapping


def createNewFieldOn(field_type, target_id, target_type, fieldId):
    if not target_type or not target_id:
        return None, None

    userId = flask.g.user
    parameter = {"FieldID": fieldId}
    if field_type == "MultiLine":
        parameter["Value"] = Create.create("Notebook", {}, get_db(), userId)
    if field_type == "ChemicalStructure":
        parameter["Value"] = Create.create("ChemicalStructure", {}, get_db(), userId)
    if field_type == "Date":
        parameter["Value"] = datetime.datetime.now()
    field_data: FieldData = Create.create("FieldData", parameter, return_document=True)

    field_data_id = field_data.id
    project_id = field_data.ProjectID.id

    category = ResearchCategory.objects(
        NameLower=target_type.lower(), ProjectID=project_id
    )
    if category:
        target_type = "researchitems"

    if target_type == "experiments":
        append("Experiment", "FieldDataIDList", target_id, field_data_id)

    if target_type == "researchitems":
        append("ResearchItem", "FieldDataIDList", target_id, field_data_id)

    if target_type == "samples":
        append("Sample", "FieldDataIDList", target_id, field_data_id)

    if target_type == "groups":
        append("Group", "FieldDataIDList", target_id, field_data_id)

    if target_type == "comboboxentries":
        append("ComboBoxEntry", "FieldDataIDList", target_id, field_data_id)

    value = "--"
    if parameter.get("Value"):
        if field_type == "Date":
            value = parameter["Value"].isoformat()
            # remove ms
            if "." in value:
                value = value.split(".")[0]

        else:
            value = str(parameter["Value"])

    return field_data_id, value
