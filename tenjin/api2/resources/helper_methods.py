import bson
import datetime
import flask
from functools import wraps
import json
from mongoengine import Q

from tenjin.database.db import get_db

from tenjin.api2.schema.response_schema import ResponseSchema, Response

from tenjin.mongo_engine.Field import Field
from tenjin.mongo_engine.ComboBoxEntry import ComboBoxEntry
from tenjin.mongo_engine.Unit import Unit

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete



def response_wrapper(func):
    """
    Wrapper to ensure that the function returns a Response object.
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        result = Response(status=True, results=result)
        return ResponseSchema().dump(result)

    return wrapped


def get_inner_data(collection, id_list):
    """returns id and name of ids in collection"""
    db = get_db().db
    cursor = db[collection].find({"_id": {"$in": id_list}}, {"Name": 1, "_id": 1})
    data_dict = {
        entry.get("_id"): entry for entry in cursor
    }
    return data_dict


def get_json_from_request() -> list:
    """Get JSON data from the request."""
    if flask.request.is_json:
        data = flask.request.get_json()
    else:
        text = flask.request.get_data(as_text=True)
        data = json.loads(text)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        return []


def get_id_list_from_request_and_check_permission(
    collection: str, args: dict, flag: str, project_id=None, only_id_allowed=False
) -> tuple[list, str]:
    """
    Checks if the user has permission to access the project and returns a list of IDs based on the provided arguments.

    Parameters
    ----------
    collection : str
        Collection name
    args : dict
        Dictionary containing the arguments parsed from webargs useing the QueryInputSchema.
    flag : str
        checking permission flag, must be "read", "write", "update" or "delete"
    project_id : _type_, optional
        ProjectID the items belong to, for Project collection this is not needed, by default None

    Returns
    -------
    List, string
        containing the IDs of the items in the collection, and a message string.

    """
    from tenjin.mongo_engine import Database
    from tenjin.mongo_engine.ResearchCategory import ResearchCategory
    from tenjin.mongo_engine.Project import Project

    assert flag in ["read", "write", "update", "delete"], AssertionError(
        "Flag must be one of 'read', 'write', 'update', or 'delete'"
    )

    id_list = args.get("id_list")
    short_id_list = args.get("short_id_list")
    name_list = args.get("name_list")
    category_name = args.get("category_name", "")
    category_id = args.get("category_id", "")
    parent_group_id = args.get("parent_group_id", "")

    cls = Database.get_collection_class(collection)
    if collection != "Project":
        if not project_id:
            raise ValueError(
                "Project ID must be provided for collections other than Project"
            )
        project_id = bson.ObjectId(project_id)
        access = Project.check_permission_to_project(project_id, flask.g.user, flag)
        if not access:
            raise PermissionError(
                f"User does not have {flag} permission for project {project_id}"
            )

    if id_list or short_id_list or name_list:
        if id_list:
            id_list = [bson.ObjectId(_id) for _id in id_list]
            if collection == "Project":
                docs = cls.objects(id__in=id_list).only("id")
            else:
                docs = cls.objects(id__in=id_list, ProjectID=project_id).only("id")
            id_list = [d.id for d in docs]
            if not id_list:
                raise ValueError("No items found with the given id")
        elif only_id_allowed:
            raise ValueError("Only id_list is allowed for this endpoint")
        elif short_id_list:
            if collection == "Project":
                docs = cls.objects(ShortID__in=short_id_list).only("id")
            else:
                docs = cls.objects(
                    ShortID__in=short_id_list, ProjectID=project_id
                ).only("id")
            id_list = [d.id for d in docs]
            if not id_list:
                raise ValueError("No items found with the given short id")
        elif name_list:
            name_lower_list = [name.lower() for name in name_list]
            if cls.__name__ == "ResearchItem":
                if not (category_name or category_id):
                    raise ValueError("Either category name or id must be given")
                docs = []
                if category_name:
                    cat = (
                        ResearchCategory.objects(
                            NameLower=category_name.lower(), ProjectID=project_id
                        )
                        .only("id")
                        .first()
                    )
                    if cat:
                        category_id = cat.id
                if category_id:
                    category_id = bson.ObjectId(category_id)
                    docs = cls.objects(
                        NameLower__in=name_lower_list, ResearchCategoryID=category_id
                    )
            elif cls.__name__ == "Group":
                if parent_group_id:
                    parent_group_id = bson.ObjectId(parent_group_id)
                    docs = cls.objects(
                        NameLower__in=name_lower_list,
                        GroupID=bson.ObjectId(parent_group_id),
                        ProjectID=project_id,
                    ).only("id")
                else:
                    docs = cls.objects(
                        NameLower__in=name_lower_list,
                        GroupID=None,
                        ProjectID=bson.ObjectId(project_id),
                    ).only("id")

            elif cls.__name__ == "Project":
                docs = cls.objects(NameLower__in=name_lower_list).only("id")
            else:
                docs = cls.objects(
                    NameLower__in=name_lower_list, ProjectID=bson.ObjectId(project_id)
                ).only("id")

            id_list = [d.id for d in docs]
            if not id_list:
                raise ValueError("No items found with the given name")
        if collection == "Project":
            new_id_list = []
            for _id in id_list:
                access = Project.check_permission_to_project(_id, flask.g.user, flag)
                if access:
                    new_id_list.append(_id)
            id_list = new_id_list
        return id_list
    else:
        return []

def write_links(item1_id, collection_1, item2_id_list, collection_2):
    from tenjin.mongo_engine.Link import Link
    # remove all links from the same type, meaning remove e.g. all links to samples if collection2 is Sample
    links = Link.objects((Q(DataID1=item1_id) & Q(Collection2=collection_2)) | (Q(DataID2=item1_id) & Q(Collection1=collection_2)))
    for link in links:
        Delete.delete("Link", link.id)
    for item2_id in item2_id_list:
        data = {"DataID1": item1_id,
                "Collection1": collection_1,
                "DataID2": item2_id,
                "Collection2": collection_2}
        link_id = Create.create("Link", data)

def get_linked_items(item_id_list):
    from tenjin.mongo_engine.Link import Link

    links = Link.objects(Q(DataID1__in=item_id_list) | Q(DataID2__in=item_id_list))
    sample_id_list = []
    researchitem_id_list = []
    exp_id_list = []
    itemId_sampleId_mapping = {}
    itemId_researchitemId_mapping = {}
    itemId_expId_mapping = {}
    for link in links:
        if link.DataID1 in item_id_list:
            item_id = link.DataID1
            if link.Collection2 == "Experiment":
                exp_id = link.DataID2
                exp_id_list.append(exp_id)
                if item_id not in itemId_expId_mapping:
                    itemId_expId_mapping[item_id] = []
                itemId_expId_mapping[item_id].append(exp_id)
            elif link.Collection2 == "Sample":
                sample_id = link.DataID2
                sample_id_list.append(sample_id)
                if item_id not in itemId_sampleId_mapping:
                    itemId_sampleId_mapping[item_id] = []
                itemId_sampleId_mapping[item_id].append(sample_id)
            elif link.Collection2 == "ResearchItem":
                researchitem_id = link.DataID2
                researchitem_id_list.append(researchitem_id)
                if item_id not in itemId_researchitemId_mapping:
                    itemId_researchitemId_mapping[item_id] = []
                itemId_researchitemId_mapping[item_id].append(researchitem_id)
        elif link.DataID2 in item_id_list:
            item_id = link.DataID2
            if link.Collection1 == "Experiment":
                exp_id = link.DataID1
                exp_id_list.append(exp_id)
                if item_id not in itemId_expId_mapping:
                    itemId_expId_mapping[item_id] = []
                itemId_expId_mapping[item_id].append(exp_id)
            elif link.Collection1 == "Sample":
                sample_id = link.DataID1
                sample_id_list.append(sample_id)
                if item_id not in itemId_sampleId_mapping:
                    itemId_sampleId_mapping[item_id] = []
                itemId_sampleId_mapping[item_id].append(sample_id)
            elif link.Collection1 == "ResearchItem":
                researchitem_id = link.DataID1
                researchitem_id_list.append(researchitem_id)
                if item_id not in itemId_researchitemId_mapping:
                    itemId_researchitemId_mapping[item_id] = []
                itemId_researchitemId_mapping[item_id].append(researchitem_id)

    return (
        exp_id_list,
        sample_id_list,
        researchitem_id_list,
        itemId_expId_mapping,
        itemId_sampleId_mapping,
        itemId_researchitemId_mapping,
    )
    

def prepare_fielddata_query_input(
    fielddata_query_list: list[dict], project_id: bson.ObjectId
):
    field_names_lower = []
    for fielddata_query in fielddata_query_list:
        if "fieldname" not in fielddata_query or "value" not in fielddata_query:
            raise ValueError("Each fielddata must contain 'fieldname' and 'value'")
        if not isinstance(fielddata_query["fieldname"], str) or not isinstance(
            fielddata_query["value"], str
        ):
            raise ValueError("'fieldname' and 'value' must be strings")
        field_names_lower.append(fielddata_query["fieldname"].lower())

    fields = Field.objects(NameLower__in=field_names_lower, ProjectID=project_id).only(
        "id", "NameLower", "Type", "ProjectID"
    )
    field_mapping = {field.NameLower: field for field in fields}

    combo_filter = []
    numeric_filter = []
    checks_filter = []
    date_filter = []
    text_filter = []
    
    type_method_mapping = {
        "ComboBox": {"method": prepare_combo, "list": combo_filter},
        "Numeric": {"method": prepare_numeric_and_numeric_range, "list": numeric_filter},
        "CheckBox": {"method": prepare_checks, "list": checks_filter},
        "Date": {"method": prepare_date, "list": date_filter},
        "SingleLine": {"method": prepare_text, "list": text_filter},
    }

    

    for fielddata_query in fielddata_query_list:
        field_name_lower = fielddata_query["fieldname"].lower()
        if field_name_lower not in field_mapping:
            raise ValueError(
                f"Field with name '{fielddata_query['fieldname']}' not found in the project"
            )
        field = field_mapping[field_name_lower]
        type_info = type_method_mapping.get(field.Type)
        if not type_info:
            raise ValueError(f"Unsupported field type: {field.Type}")

        method = type_info["method"]
        filter_list = type_info["list"]
        filter_list.append(method(fielddata_query, field))

    return {
        "combo": combo_filter,
        "numeric": numeric_filter,
        "checkbox": checks_filter,
        "date": date_filter,
        "singleline": text_filter,
    }


def prepare_combo(fielddata_query, field):
        comboboxentries = ComboBoxEntry.objects(FieldID=field.id).only(
            "id", "Name", "NameLower"
        )
        combo_mapping_name = {entry.NameLower: entry for entry in comboboxentries}
        combo_mapping_id = {entry.id: entry for entry in comboboxentries}
        value = fielddata_query["value"]
        combo_id_list = []
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
            value_list = value.split(",")
        else:
            value_list = [value]
        for v in value_list:
            while v.startswith(" "):
                v = v[1:]
            while v.endswith(" "):
                v = v[:-1]
            try:
                v = bson.ObjectId(v)
                if v in combo_mapping_id:
                    combo_id_list.append({"id": v})
            except:
                if str(v).lower() in combo_mapping_name:
                    combo = combo_mapping_name[str(v).lower()]
                    combo_id_list.append({"id": combo.id})

        value_dict = {"field": field.id, "values": combo_id_list}
        return value_dict

def prepare_numeric_and_numeric_range(fielddata_query, field):
    value = fielddata_query["value"]
    unit = None
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(
            f"Value '{value}' is not a valid range. It must be enclosed in square brackets."
        )

    value = value[1:-1]
    value_list = value.split(",")
    if not len(value_list) >= 2:
        raise ValueError(
            f"Value '{value}' is not a valid range. It must contain at least two values."
        )
        
    value_min = value_list[0]
    while value_min.startswith(" "):
        value_min = value_min[1:]
    while value_min.endswith(" "):
        value_min = value_min[:-1]
    
    value_max = value_list[1]
    while value_max.startswith(" "):
        value_max = value_max[1:]
    while value_max.endswith(" "):
        value_max = value_max[:-1]
        
    unit = value_list[2] if len(value_list) > 2 else None
    if unit:
        while unit.startswith(" "):
            unit = unit[1:]
        while unit.endswith(" "):
            unit = unit[:-1]

        project_id = field.ProjectID.id
        try:
            unit = bson.ObjectId(unit)
            query = Q(id=unit, ProjectID=project_id) | Q(id=unit, Predefined=True)
            unit = Unit.objects(query).only("id").first()
        except:
            query = Q(ShortName=unit, ProjectID=project_id) | Q(
                ShortName=unit, Predefined=True
            )
            unit = Unit.objects(query).only("id").first()
        if unit is None:
            raise ValueError(
                f"Unit '{unit}' not found in the project or predefined units"
            )

    try:
        value_min = float(value_min)
    except:
        raise ValueError(f"Value '{value_min}' is not a valid number")
    try:
        value_max = float(value_max)
    except:
        raise ValueError(f"Value '{value_max}' is not a valid number")

    value_dict = {
        "field": field.id,
        "min": value_min,
        "max": value_max,
        "unit": unit.id if unit else None,
    }
    return value_dict

def prepare_checks(fielddata_query, field):
    value = fielddata_query["value"]
    if value.lower() in ["true", "1", "yes"]:
        value = True
    elif value.lower() in ["false", "0", "no"]:
        value = False
    else:
        raise ValueError(f"Value '{value}' is not a valid boolean")

    return {"field": field.id, "value": value}


def prepare_date(fielddata_query, field):
    value = fielddata_query["value"]
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(
            f"Value '{value}' is not a valid date range. It must be enclosed in square brackets."
        )

    value = value[1:-1]
    value_list = value.split(",")
    if not len(value_list) == 2:
        raise ValueError(
            f"Value '{value}' is not a valid date range. It must contain at two values."
        )
        
    value_start = value_list[0]
    while value_start.startswith(" "):
        value_start = value_start[1:]
    while value_start.endswith(" "):
        value_start = value_start[:-1]
        
    value_end = value_list[1]
    while value_end.startswith(" "):
        value_end = value_end[1:]
    while value_end.endswith(" "):
        value_end = value_end[:-1]

    try:
        # only test for valid format
        datetime.datetime.fromisoformat(value_start)
    except:
        raise ValueError(f"Value '{value_start}' is not a valid date. It must be send in iso-format")

    try:
        datetime.datetime.fromisoformat(value_end)
    except:
        raise ValueError(f"Value '{value_end}' is not a valid date. It must be send in iso-format")

    value_dict = {
        "field": field.id,
        "min": value_start,
        "max": value_end,
        "option": "custom"
    }
    return value_dict

def prepare_text(fielddata_query, field):
    value = fielddata_query["value"]
    if not isinstance(value, str):
        raise ValueError(f"Value '{value}' is not a valid text. It must be a string.")

    return {"field": field.id, "value": value}

