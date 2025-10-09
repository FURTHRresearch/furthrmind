import bson
import datetime
import flask
from webargs.flaskparser import use_args
from mongoengine import Q
from typing import List
from datetime import timezone

from tenjin.api2.resources.field import (
    check_field_by_name_and_create_if_not_exists,
)
from tenjin.api2.resources.helper_methods import response_wrapper, get_json_from_request
from tenjin.api2.schema.fielddata_schema import FieldDataPostSchema
from tenjin.api2.schema.fielddata_schema import FieldDataSchema

from tenjin.execution.update import Update
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete

from tenjin.mongo_engine.ComboBoxEntry import ComboBoxEntry
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.Field import Field
from tenjin.mongo_engine.FieldData import FieldData
from tenjin.mongo_engine.Unit import Unit

from tenjin.database.db import get_db


bp = flask.Blueprint("api2/fielddata", __name__)


def update_or_create_fielddata_method(args: dict, project_id: bson.ObjectId) -> bson.ObjectId:
    """
    Process field data from any other collection.
    """
    if "_id" not in args:
        if args.get("field_id") is None:
            field_name = args.get("field_name")
            if not field_name:
                raise ValueError("Field name is required.")
            field_type = args.get("field_type")
            field_id = check_field_by_name_and_create_if_not_exists(
                field_name, field_type, project_id
            )
        else:
            field_id = bson.ObjectId(args["field_id"])
            field = Field.objects(id=field_id, ProjectID=project_id).first()
            if not field:
                raise ValueError("Field not found.")
        fielddata_id = create_fielddata(field_id)

        args["_id"] = fielddata_id

    if "_id" in args:
        fielddata_id = bson.ObjectId(args["_id"])
        if "value" in args:
            update_fielddata_value(fielddata_id, project_id, args["value"])

        if "unit" in args:
            unit_dict = args["unit"]
            update_fielddata_unit(fielddata_id, unit_dict, project_id)

    return fielddata_id


def update_fielddata_value(fielddata_id, project_id, value) -> bool:
    fielddata = FieldData.objects(id=fielddata_id, ProjectID=project_id).first()
    if not fielddata:
        raise ValueError("Field data not found.")

    field_type = fielddata.Type
    if field_type == "ComboBox":
        value = check_and_create_combobox_entry(value, fielddata)
    if field_type in [
        "Numeric",
        "NumericRange",
        "Date",
        "CheckBox",
        "ComboBox",
        "SingleLine",
    ]:
        update_fielddata_value_direct(fielddata_id, value, field_type)
    elif field_type in ["MultiLine"]:
        update_or_create_notebook(fielddata, value)
    elif field_type in ["RawDataCalc", "Calculation"]:
        return fielddata_id


def check_and_create_combobox_entry(value, fielddata):
    if value is None:
        return None
    field_id = fielddata.FieldID.id
    if isinstance(value, dict):
        combo_id = None
        if "id" in value:
            combo_id = bson.ObjectId(value["id"])
            combo = ComboBoxEntry.objects(id=combo_id, FieldID=field_id).first()
            if not combo:
                raise ValueError(f"ComboBoxEntry with id '{value['id']}' not found.")
            return combo_id
        if "name" in value:
            name = value["name"]
            combo_id = check_combobox_name_and_create_if_not_exists(name, field_id)
            return combo_id
    elif isinstance(value, str):
        name = value
        combo_id = check_combobox_name_and_create_if_not_exists(name, field_id)
        return combo_id
    else:
        raise ValueError("Invalid ComboBox value format.")


def check_combobox_name_and_create_if_not_exists(name, field_id):
    combo_entry = ComboBoxEntry.objects(
        NameLower=name.lower(), FieldID=field_id
    ).first()
    if not combo_entry:
        parameter = {"Name": name, "FieldID": field_id}
        combo_id = Create.create("ComboBoxEntry", parameter)
    else:
        combo_id = combo_entry.id
    return combo_id


def update_fielddata_value_direct(fielddata_id, value, field_type):
    value_max = None
    if field_type == "Numeric":
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                raise ValueError("Invalid numeric value provided.")
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a numeric type.")
    elif field_type == "NumericRange":
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError(
                "NumericRange value must be a list with two numeric values."
            )
        value_min = None
        for pos, v in enumerate(value):
            if v is None:
                continue
            if isinstance(v, str):
                try:
                    v = float(v)
                except ValueError:
                    raise ValueError("Invalid numeric value provided in NumericRange.")
            if not isinstance(v, (int, float)):
                raise ValueError("Both values in NumericRange must be numeric.")
            if pos == 0:
                value_min = v
            elif pos == 1:
                value_max = v
        value = value_min
    elif field_type == "Date":
        if isinstance(value, str):
            try:
                value = datetime.datetime.fromisoformat(value)
            except:
                raise ValueError("date time must be send as iso format")

        elif isinstance(value, (int, float)):
            try:
                value = int(value)
                value = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
            except:
                raise ValueError("date time must be send as unix time in seconds")
        else:
            raise ValueError(
                "date time must be send as iso format or unix time in seconds"
            )

    Update.update("FieldData", "Value", value, fielddata_id)
    if field_type == "NumericRange":
        Update.update("FieldData", "ValueMax", value_max, fielddata_id)


def update_or_create_notebook(fielddata, value):
    notebook_id = fielddata.Value
    fielddata_id = fielddata.id
    field_id = fielddata.FieldID.id
    if notebook_id is None:
        notebook_id = create_notebook(field_id)
        Update.update("FieldData", "Value", notebook_id, fielddata_id)

    if not isinstance(value, (str, dict)):
        raise ValueError("MultiLine value must be a string or a dictionary.")

    if isinstance(value, str):
        notebook_id = Update.update("Notebook", "Content", value, notebook_id)
    elif isinstance(value, dict):
        if "content" in value:
            notebook_id = Update.update(
                "Notebook", "Content", value["content"], notebook_id
            )
        else:
            raise ValueError("MultiLine value dictionary must contain 'content' key.")


def create_notebook(field_id) -> bson.ObjectId:
    field = Field.objects(id=field_id).first()
    if not field:
        raise ValueError("Field not found.")
    parameter = {"ProjectID": field.ProjectID.id}
    notebook_id = Create.create("Notebook", parameter)
    return notebook_id


def create_fielddata(field_id):
    parameter = {"FieldID": field_id}
    fielddata_id = Create.create("FieldData", parameter)
    return fielddata_id


def update_fielddata_unit(
    fielddata_id, unit_dict: None | dict, project_id: bson.ObjectId = None
):  
    fielddata = FieldData.objects(id=fielddata_id, ProjectID=project_id).first()
    if not fielddata:
        raise ValueError("Field data not found.")

    if fielddata.Type not in ["Numeric", "NumericRange"]:
        raise ValueError("Field data type must be Numeric or NumericRange for unit updates.")

    if unit_dict is None:
        Update.update("FieldData", "UnitID", None, fielddata_id)
        return

    unit = None
    if "id" in unit_dict:
        try:
            unit_id = bson.ObjectId(unit_dict["id"])
        except bson.errors.InvalidId:
            raise ValueError("Invalid ObjectId format.")
        query = Q(id=unit_id) & Q(ProjectID=project_id) | Q(id=unit_id) & Q(
            Predefined=True
        )
        unit = Unit.objects(id=unit_id).first()
        if not unit:
            raise ValueError(
                f"Unit with id '{unit_dict['id']}' not found in this project."
            )

    elif "ShortName" in unit_dict:
        query = Q(ShortName=unit_dict["ShortName"]) & Q(
            ProjectID=project_id
        ) | Q(ShortName=unit_dict["ShortName"]) & Q(Predefined=True)
        unit = Unit.objects(query).first()
        if not unit:
            raise ValueError(
                f"Unit with ShortName '{unit_dict['ShortName']}' not found in this project."
            )
    if unit is None:
        raise ValueError("Unit dictionary must contain 'id' or 'ShortName' key.")

    unit_id = unit.id
    Update.update("FieldData", "UnitID", unit_id, fielddata_id)


def get_fielddata_method(project_id: str, fielddata_id_list: List[str]):
    result = []
    mongoClient = get_db().db
    fieldDataCursor = mongoClient["FieldData"].find(
        {"_id": {"$in": fielddata_id_list}, "ProjectID": bson.ObjectId(project_id)}
    )
    fieldCursor = mongoClient["Field"].find(
        {"_id": {"$in": fieldDataCursor.distinct("FieldID")}}
    )
    fieldDict = {field.get("_id"): field for field in fieldCursor}
    unitCursor = mongoClient["Unit"].find(
        {"_id": {"$in": fieldDataCursor.distinct("UnitID")}}
    )
    unitDict = {unit.get("_id"): unit for unit in unitCursor}
    authorList = getAuthor(fieldDataCursor.distinct("AuthorID"), mongoClient)
    authorDict = {a["_id"]: a for a in authorList}
    valueList = [
        entry
        for entry in fieldDataCursor.distinct("Value")
        if isinstance(entry, bson.ObjectId)
    ]
    typeList = fieldCursor.distinct("Type")
    valueDict = {}

    if "MultiLine" in typeList:
        cursor = mongoClient["Notebook"].find(
            {"_id": {"$in": valueList}}, {"Content": 1, "_id": 1}
        )
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "content": entry.get("Content"),
                }
                for entry in cursor
            }
        )
    if "User" in typeList:
        cursor = mongoClient["User"].find(
            {"_id": {"$in": valueList}}, {"LastName": 1, "FirstName": 1, "_id": 1}
        )
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "name": f'{entry.get("FirstName")}{entry.get("LastName")}',
                }
                for entry in cursor
            }
        )
    if "File" in typeList:
        cursor = mongoClient["File"].find(
            {"_id": {"$in": valueList}}, {"Name": 1, "_id": 1}
        )
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "name": entry.get("Name"),
                }
                for entry in cursor
            }
        )
    if "ComboBox" in typeList or "ComboBoxSynonym" in typeList:
        cursor = mongoClient["ComboBoxEntry"].find(
            {"_id": {"$in": valueList}}, {"Name": 1, "_id": 1}
        )
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "name": entry.get("Name"),
                }
                for entry in cursor
            }
        )
    if "Link" in typeList:
        cursor = mongoClient["FieldDataLink"].find(
            {"_id": {"$in": valueList}},
            {"TargetCollection": 1, "TargetID": 1, "_id": 1},
        )
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "link": entry.get("TargetCollection"),
                    "targetid": entry.get("TargetID"),
                }
                for entry in cursor
            }
        )
    if "ChemicalStructure" in typeList:
        cursor = mongoClient["ChemicalStructure"].find({"_id": {"$in": valueList}})
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "inchi": entry.get("InChI"),
                    "inchikey": entry.get("InChIKey"),
                    "smiles": entry.get("Smiles"),
                    "molfile": entry.get("MolfileString"),
                }
                for entry in cursor
            }
        )
    if "Calculation" in typeList or "RawDataCalc" in typeList:
        cursor = mongoClient["Calculation"].find(
            {"_id": {"$in": valueList}}, {"Output": 1, "_id": 1}
        )
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "result": entry.get("Output"),
                }
                for entry in cursor
            }
        )
    if "Table" in typeList:
        cursor = mongoClient["Table"].find(
            {"_id": {"$in": valueList}}, {"ColumnIDList": 1, "Name": 1, "_id": 1}
        )
        valueDict.update(
            {
                entry.get("_id"): {
                    "id": str(entry.get("_id")),
                    "name": entry.get("Name"),
                    "columnids": entry.get("ColumnIDList"),
                }
                for entry in cursor
            }
        )

    for fieldData in fieldDataCursor:
        field = fieldDict.get(fieldData.get("FieldID"), {})
        unit = unitDict.get(fieldData.get("UnitID"), None)
        value = fieldData.get("Value")
        value_max = fieldData.get("ValueMax")
        si_value = fieldData.get("SIValue")
        si_value_max = fieldData.get("SIValueMax")
        if isinstance(value, bson.ObjectId):
            value = valueDict.get(value, None)
        elif isinstance(value, datetime.datetime):
            # value = value.replace(tzinfo=datetime.timezone.utc)
            # value = value.timestamp()
            value = value.isoformat()
        try:
            author = (
                authorDict[fieldData["AuthorID"]] if fieldData["AuthorID"] else None
            )
        except:
            author = None
        current_result = dict(fieldData)
        current_result.update(
            {
                "fieldname": field.get("Name"),
                "si_value": si_value,
                "unit": unit,
                "author": author,
                "value": value,
            }
        )
        if field.get("Type") == "NumericRange":
            value = [value, value_max]
            current_result["value"] = value
            si_value = [si_value, si_value_max]
            current_result["si_value"] = si_value
        result.append(current_result)

    return result


def getAuthor(authorIDList, mongoClient):
    result = []
    authorCursor = mongoClient["Author"].find({"_id": {"$in": authorIDList}})
    for author in authorCursor:
        result.append(author)
    return result


@bp.route("/<project_id>/fielddata/<fielddata_id>", methods=["GET"])
@response_wrapper
def get_fielddata(project_id: str, fielddata_id: str):
    """
    Get field data by ID
    ---
    """
    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    try:
        fielddata_id = bson.ObjectId(fielddata_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid field data ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read field data in this project."
        )

    results = get_fielddata_method(project_id, [fielddata_id])
    result = results[0] if results else None
    if not result:
        raise ValueError("Field data not found.")
    dumped_result = FieldDataSchema().dump(result)
    return dumped_result


@bp.route("/<project_id>/fielddata", methods=["POST"])
@response_wrapper
def post(project_id: str):
    """
    Create a new group
    ---
    """

    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="write")
    if not access:
        PermissionError(
            "You do not have permission to create or update a fielddata in this project."
        )
    data_list = get_json_from_request()
    data_list = FieldDataPostSchema().load(data_list, many=True)
    return_id_list = []
    for data in data_list:
        fielddata_id = update_or_create_fielddata_method(data, project_id)
        return_id_list.append(fielddata_id)
    return return_id_list


@bp.route("/<project_id>/fielddata/<fielddata_id>", methods=["DELETE"])
@response_wrapper
def delete(project_id: str, fielddata_id: str):
    """
    Delete a field data by ID
    ---
    """
    from mongo_engine.Project import Project
    from mongo_engine.Group import Group

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(
        project_id, flask.g.user, flag="delete"
    )
    if not access:
        PermissionError("You do not have permission to delete this field data.")

    fielddata_id = bson.ObjectId(fielddata_id)
    fielddata = FieldData.objects(id=fielddata_id, ProjectID=project_id).first()
    if not fielddata:
        raise ValueError("Field data not found.")

    Delete.delete("FieldData", fielddata_id)

    return fielddata_id
