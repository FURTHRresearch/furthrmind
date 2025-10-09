import datetime
import json
import operator
import os
from io import BytesIO

import bson
import flask
from PIL import Image
from bson import json_util
from flask import request
from mongoengine.queryset import Q

from tenjin.file.file_storage import FileStorage
from tenjin.execution.append import Append
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete
from tenjin.execution.pop import Pop
from tenjin.database.db import get_db
from .auth import login_required
from .helper.fieldsHelper import getFields, get_field_data_values
from .helper.furthrHelper import ensureAccess
from .helper.filter_utils import get_linked_items_recursive

bp = flask.Blueprint("webresearchitems", __name__)


@bp.route("/item/<type>/<id>", methods=["POST"])
@login_required
def item_update(type, id):
    from tenjin.mongo_engine.Link import Link
    from tenjin.mongo_engine.Experiment import Experiment
    from tenjin.mongo_engine.Sample import Sample
    from tenjin.mongo_engine.ResearchItem import ResearchItem

    if type.lower() == "experiments":
        collection = "Experiment"
    elif type.lower() == "samples":
        collection = "Sample"
    elif type.lower() == "groups":
        collection = "Group"
    elif type.lower() == "comboboxentries":
        collection = "ComboBoxEntry"
    else:
        collection = "ResearchItem"

    ensureAccess(collection, "write", id)
    data = flask.request.get_json()
    userId = flask.g.user
    itemId = bson.ObjectId(id)
    if "neglect" in data:
        Update.update(
            collection, "Neglect", data["neglect"], itemId, get_db(), userId
        )  # do we need more validation?
    elif "protected" in data:
        Update.update(
            collection, "Protected", data["protected"], itemId, get_db(), userId
        )
    elif "name" in data:
        result = Update.update(
            collection, "Name", data["name"], itemId, get_db(), userId
        )
    elif "linked_items" in data:
        # remove old links:
        id_list = [bson.ObjectId(s["id"]) for s in data["linked_items"]]
        links = Link.objects(
            (Q(DataID1=itemId) & Q(DataID2__nin=id_list))
            | (Q(DataID2=itemId) & Q(DataID1__nin=id_list))
        )
        for link in links:
            Delete.delete("Link", link.id)

        links = Link.objects(
            (Q(DataID1=itemId) & Q(DataID2__in=id_list))
            | (Q(DataID2=itemId) & Q(DataID1__in=id_list))
        )
        existing_link_list = []
        for link in links:
            if link.DataID1 == itemId:
                existing_link_list.append(link.DataID2)
            else:
                existing_link_list.append(link.DataID1)

        samples = Sample.objects(id__in=id_list)
        for sample in samples:
            if sample.id in existing_link_list:
                continue
            data_dict = {
                "DataID1": itemId,
                "Collection1": collection,
                "DataID2": sample.id,
                "Collection2": "Sample",
            }
            Create.create("Link", data_dict)

        research_items = ResearchItem.objects(id__in=id_list)
        for item in research_items:
            if item.id in existing_link_list:
                continue
            data_dict = {
                "DataID1": itemId,
                "Collection1": collection,
                "DataID2": item.id,
                "Collection2": "ResearchItem",
            }
            Create.create("Link", data_dict)

        exps = Experiment.objects(id__in=id_list)
        for exp in exps:
            if exp.id in existing_link_list:
                continue
            data_dict = {
                "DataID1": itemId,
                "Collection1": collection,
                "DataID2": exp.id,
                "Collection2": "Experiment",
            }
            Create.create("Link", data_dict)

    elif "fields" in data:
        Update.update(
            collection,
            "FieldDataIDList",
            [bson.ObjectId(f) for f in data["fields"]],
            itemId,
            get_db(),
            userId,
        )
    return "all done"


@bp.route("/project/<project_id>/item/<item_type>/<item_id>/check", methods=["POST"])
@login_required
def item_check_name_update(project_id, item_type, item_id):
    data = request.get_json()
    name = data.get("name")
    group_id = data.get("group_id")
    category_id = data.get("category_id")
    check = check_item(project_id, item_type, name, item_id, group_id, category_id)
    if check:
        return "True"
    else:
        return "False"


@bp.route("/project/<project_id>/item/<item_type>/check", methods=["POST"])
@login_required
def item_check_name_create(project_id, item_type):
    data = request.get_json()
    name = data.get("name")
    group_id = data.get("group_id")
    category_id = data.get("category_id")
    check = check_item(
        project_id, item_type, name, group_id=group_id, category_id=category_id
    )
    if check:
        return "True"
    else:
        return "False"


def check_item(
    project_id, item_type, new_name, item_id=None, group_id=None, category_id=None
):
    from tenjin.mongo_engine import Database

    param = {"Name": new_name, "ProjectID": bson.ObjectId(project_id)}
    if item_type.lower() == "experiments":
        collection = "Experiment"
        param["GroupIDList"] = [bson.ObjectId(group_id)]
    elif item_type.lower() == "samples":
        collection = "Sample"
        param["GroupIDList"] = [bson.ObjectId(group_id)]
    elif item_type.lower() in ["groups", "subgroups"]:
        collection = "Group"
        if group_id:
            param["GroupID"] = bson.ObjectId(group_id)
    else:
        collection = "ResearchItem"
        param["ResearchCategoryID"] = bson.ObjectId(category_id)

    if item_id:
        cls, doc = Database.get_collection_class_and_document(
            collection, bson.ObjectId(item_id)
        )
        doc.Name = new_name
    else:
        cls = Database.get_collection_class(collection)
        doc = cls(**param)
    try:
        doc.validate(clean=True)
        return True
    except:
        return False


@bp.route("/projects/<projid>/item/<type>/<itemid>/fields", methods=["POST"])
@login_required
def item_add_field(projid, type, itemid):
    if type.lower() == "experiments":
        collection = "Experiment"
    elif type.lower() == "samples":
        collection = "Sample"
    elif type.lower() == "groups":
        collection = "Group"
    elif type.lower() == "comboboxentries":
        collection = "ComboBoxEntry"
    else:
        collection = "ResearchItem"

    userId = flask.g.user
    db = get_db().db
    data = flask.request.get_json()
    name = data["name"] if "name" in data else ""
    field = db.Field.find_one(
        {"$and": [{"Name": name}, {"ProjectID": bson.ObjectId(projid)}]}
    )
    if not field:
        flask.abort(404)
    parameter = {"FieldID": field["_id"]}
    if field["Type"] == "MultiLine":
        parameter["Value"] = Create.create(
            "Notebook", {"ProjectID": bson.ObjectId(projid)}, get_db(), userId
        )
    if field["Type"] == "ChemicalStructure":
        parameter["Value"] = Create.create("ChemicalStructure", {}, get_db(), userId)
    if field["Type"] == "Date":
        current_date = datetime.datetime.now()
        current_date = current_date.replace(microsecond=0)
        parameter["Value"] = current_date

    fieldDataId = Create.create("FieldData", parameter, get_db(), userId)

    Append.append(collection, "FieldDataIDList",
                  bson.ObjectId(itemid), fieldDataId)
    
    value = "--"
    if parameter.get("Value", None):
        if field["Type"] == "Date":
            value = parameter["Value"].isoformat()
            # remove milliseconds
            if "." in value:
                value = value.split(".")[0]
        else:
            value = str(parameter["Value"])

    return {
        "id": str(fieldDataId),
        "Name": name,
        "FieldID": str(field["_id"]),
        "Value": value,
        "UnitID": "--",
        "Type": field["Type"],
        "calculationType": "WebDataCalc",
        "smiles": "",
        "cdxml": "",
    }


@bp.route("/item/<type>/<id>/fields", methods=["PUT"])
@login_required
def item_update_field(type, id):
    if type.lower() == "experiments":
        collection = "Experiment"
    elif type.lower() == "samples":
        collection = "Sample"
    elif type.lower() == "groups":
        collection = "Group"
    elif type.lower() == "comboboxentries":
        collection = "ComboBoxEntry"
    else:
        collection = "ResearchItem"
    # switch order of fields, not possible currently for combobox entry (GUI wise)

    ensureAccess(collection, "write", id)
    data = flask.request.get_json()
    userId = flask.g.user
    itemId = bson.ObjectId(id)
    Update.update(collection, "FieldDataIDList",
                  data.get('fieldDataIds'), itemId)
    return 'all good'

@bp.route('/projects/<project_id>/fielddata/<fielddata_id>', methods=['Delete'])
@login_required
def remove_field_from_item(project_id, fielddata_id):
    import time
    start = time.time()
    from tenjin.execution.delete import Delete
    fielddata_id = bson.ObjectId(fielddata_id)
    Delete.delete("FieldData", fielddata_id, include_attributes=["ParentCollection", "ParentDataID"])
    print("Time to delete field data: ", time.time() - start)
    return "all good"
        

@bp.route("/item/<type>/<id>", methods=["DELETE"])
@login_required
def item_delete(type, id):
    if type.lower() == "experiments":
        collection = "Experiment"
    elif type.lower() == "samples":
        collection = "Sample"
    elif type.lower() == "groups":
        collection = "Group"
    elif type.lower() == "comboboxentries":
        collection = "ComboBoxEntry"
    else:
        collection = "ResearchItem"

    ensureAccess(collection, "delete", id)
    Delete.delete(collection, bson.ObjectId(id))

    return "all done"


@bp.route("/item/samples/<id>", methods=["GET"])
@login_required
def get_sample(id):
    ensureAccess("Sample", "read", id)
    sampleId = bson.ObjectId(id)
    return bson.json_util.dumps(get_sample_internal(sampleId))


def get_sample_internal(sampleId, table=False, get_linked=True):
    from tenjin.mongo_engine.RawData import RawData
    from tenjin.mongo_engine import Sample

    db = get_db().db
    s = db.Sample.find_one({"_id": sampleId})
    sample = {
        "id": str(s["_id"]),
        "Name": s["Name"],
        "FieldDataIDList": s["FieldDataIDList"],
        "FileIDList": s["FileIDList"],
        "Neglect": s["Neglect"],
        "Protected": s["Protected"],
        "shortId": s["ShortID"],
        "typeName": "Sample",
    }
    rawdata = []
    for r in RawData.objects(SampleID=bson.ObjectId(sample["id"])).order_by("Name"):
        rawdata.append({"id": str(r.id), "name": r.Name})
    sample["rawdata"] = rawdata
    sample["fields"] = getFields(sample["FieldDataIDList"], table)

    sample["linked_items"] = []
    if get_linked:
        linked_items = get_linked_items(s["_id"])
        sample["linked_items"] = linked_items

    sample["files"] = [
        {
            "id": str(f["_id"]),
            "Name": f["Name"],
            "Thumbnail": (
                str(f.get("ThumbnailFileID", ""))
                if f.get("ThumbnailFileID", "")
                else ""
            ),
        }
        for f in db.File.find({"_id": {"$in": sample["FileIDList"]}})
    ]

    spreadsheet_info = get_spreadsheet_info(s["_id"], "Sample")
    sample.update(spreadsheet_info)

    userId = flask.g.user
    sample["writable"] = Sample.check_permission_to_project(
        s["ProjectID"], bson.ObjectId(userId), "write"
    )
    sample["admin"] = Sample.check_permission_to_project(
        s["ProjectID"], bson.ObjectId(userId), "invite"
    )
    # Authentification.hasAccess(
    #         "Sample", "write", sampleId, userId, get_db())
    return sample


@bp.route("/item/<_type>/<_id>")
@login_required
def get_researchitem_route(_type, _id):
    try:
        bson.ObjectId(_id)
    except:
        flask.abort(400)
    ensureAccess("ResearchItem", "read", _id)
    return bson.json_util.dumps(get_researchitem(_id))


@bp.route("/items/field-value", methods=["POST"])
@login_required
async def get_all_item_table_method():

    data = flask.request.get_json()
    item_id_list = data.get("item_id_list")
    field_id_list = data.get("field_id_list")
    include_linked = data.get("include_linked", "None")

    from tenjin.mongo_engine.Experiment import Experiment
    from tenjin.mongo_engine.ResearchItem import ResearchItem
    from tenjin.mongo_engine.Sample import Sample

    try:
        item_id_list = [bson.ObjectId(i) for i in item_id_list]
    except:
        flask.abort(400)

    try:
        field_id_list = [bson.ObjectId(i) for i in field_id_list]
    except:
        flask.abort(400)

    field_data_id_item_id_mapping = {}
    item_id_field_data_id_mapping = {}
    field_data_id_list = []
    extra_items, total_linked_mapping = await get_linked_items_recursive(
        include_linked, item_id_list, retrieve_linked_mapping=True)
    
    item_id_list_extended = item_id_list + list(extra_items)
    item_id_list_extended = list(set(item_id_list_extended))
    
    number_of_layer = 0
    for item_id in total_linked_mapping:
        number_of_layer = len(total_linked_mapping[item_id])
        break
     
    exps = Experiment.objects(id__in=item_id_list_extended).only("FieldDataIDList", "id")
    for exp in exps:
        item_id_field_data_id_mapping[exp.id] = []
        for field_data in exp.FieldDataIDList:
            field_data_id_list.append(field_data.id)
            field_data_id_item_id_mapping[field_data.id] = exp.id
            item_id_field_data_id_mapping[exp.id].append(field_data.id)

    samples = Sample.objects(id__in=item_id_list_extended).only("FieldDataIDList", "id")
    for sample in samples:
        item_id_field_data_id_mapping[sample.id] = []
        for field_data in sample.FieldDataIDList:
            field_data_id_list.append(field_data.id)
            field_data_id_item_id_mapping[field_data.id] = sample.id
            item_id_field_data_id_mapping[sample.id].append(field_data.id)
            
    items = ResearchItem.objects(id__in=item_id_list_extended).only("FieldDataIDList", "id")
    for item in items:
        item_id_field_data_id_mapping[item.id] = []
        for field_data in item.FieldDataIDList:
            field_data_id_list.append(field_data.id)
            field_data_id_item_id_mapping[field_data.id] = item.id
            item_id_field_data_id_mapping[item.id].append(field_data.id)

    field_data_mapping = get_field_data_values(field_data_id_list, field_id_list)

    result_dict = {}
    
    def add_to_result_dict(_item_id, _field_id, value) :
        _item_id = str(_item_id)
        _field_id = str(_field_id)
        if _item_id not in result_dict:
            result_dict[_item_id] = {}
        item_value = result_dict[_item_id].get(_field_id)
        if item_value is None:
            result_dict[_item_id][_field_id] = value
        else:
            
            if isinstance(item_value, list):
                item_value.append(value)
            else:
                result_dict[_item_id][_field_id] = [
                    item_value,
                    value,
                ]
    for item_id in item_id_list:
        for layer_number in range(0, number_of_layer + 1):     
            if layer_number == 0:
                linked_items = [item_id]
            else:
                linked_items = total_linked_mapping[item_id][layer_number - 1]
            
            for field_id in field_id_list:
                # check if result is already in result_dict from previous layer
                if str(item_id) in result_dict:
                    if result_dict[str(item_id)].get(str(field_id)) is not None:
                        continue
                for _id in linked_items:
                    for field_data_id in item_id_field_data_id_mapping[_id]:
                        if field_data_id in field_data_mapping:
                            field_data = field_data_mapping[field_data_id]
                            if str(field_id) == str(field_data["field_id"]):
                                add_to_result_dict(item_id, field_id, field_data)
   
    for item_id in result_dict:
        for field_id in result_dict[item_id]:
            if isinstance(result_dict[item_id][field_id], list):
                result_dict[item_id][field_id] = prepare_mean_value_field_data(
                    result_dict[item_id][field_id]
                )

    return result_dict


def get_researchitem(id, table=False, get_linked=True):
    from tenjin.mongo_engine.ResearchItem import ResearchItem
    from tenjin.mongo_engine.RawData import RawData

    try:
        bson.ObjectId(id)
    except:
        flask.abort(400)
    db = get_db().db
    item = db.ResearchItem.find_one({"_id": bson.ObjectId(id)})

    ri = {
        "id": str(item["_id"]),
        "Name": item["Name"],
        "FieldDataIDList": item["FieldDataIDList"],
        "FileIDList": item["FileIDList"],
        "shortId": item["ShortID"],
        "Protected": item["Protected"],
    }

    category = db.ResearchCategory.find_one({"_id": item["ResearchCategoryID"]})
    ri["typeName"] = category["Name"]
    rawdata = []
    for r in RawData.objects(ResearchItemID=bson.ObjectId(ri["id"])).order_by("Name"):
        rawdata.append({"id": str(r.id), "name": r.Name})
    ri["rawdata"] = rawdata
    ri["fields"] = getFields(ri["FieldDataIDList"], table)
    ri["files"] = [
        {
            "id": str(f["_id"]),
            "Name": f["Name"],
            "Thumbnail": (
                str(f.get("ThumbnailFileID", ""))
                if f.get("ThumbnailFileID", "")
                else ""
            ),
        }
        for f in db.File.find({"_id": {"$in": ri["FileIDList"]}})
    ]

    userId = flask.g.user
    ri["writable"] = ResearchItem.check_permission_to_project(
        item["ProjectID"], bson.ObjectId(userId), "write"
    )
    ri["admin"] = ResearchItem.check_permission_to_project(
        item["ProjectID"], bson.ObjectId(userId), "invite"
    )
    ri["linked_items"] = []
    if get_linked:
        linked_items = get_linked_items(item["_id"])
        ri["linked_items"] = linked_items

    spreadsheet_info = get_spreadsheet_info(item["_id"], "ResearchItem")
    ri.update(spreadsheet_info)

    return ri


@bp.route("/item/experiments/<id>")
@login_required
def get_experiment_route_card(id):
    try:
        bson.ObjectId(id)
    except:
        flask.abort(400)
    ensureAccess("Experiment", "read", id)
    return bson.json_util.dumps(get_experiment(id, table=False))


def get_experiment_table_method(id_list, field_id):
    exps = get_db().db.Experiment.find(
        {"_id": {"$in": id_list}}, {"FieldDataIDList": 1, "_id": 1}
    )

    field_data_id_list = []
    field_data_id_exp_id_mapping = {}
    for exp in exps:
        for field_data_id in exp["FieldDataIDList"]:
            field_data_id_exp_id_mapping[field_data_id] = exp["_id"]
            field_data_id_list.append(field_data_id)

    field_data_mapping = get_field_data_values(field_data_id_list, field_id)
    exp_dict = {}

    for field_data_id in field_data_mapping:
        exp_id = field_data_id_exp_id_mapping[field_data_id]
        exp_value = exp_dict.get(str(exp_id))
        if exp_value is None:
            exp_dict[str(exp_id)] = field_data_mapping[field_data_id]
        elif isinstance(exp_value, list):
            exp_value.append(field_data_mapping[field_data_id])
        else:
            exp_dict[str(exp_id)] = [exp_value, field_data_mapping[field_data_id]]

    return exp_dict


def get_experiment(id, table=False, get_linked=True):
    from tenjin.mongo_engine.RawData import RawData
    from tenjin.mongo_engine.Experiment import Experiment

    try:
        bson.ObjectId(id)
    except:
        flask.abort(400)
    db = get_db().db
    e = db.Experiment.find_one({"_id": bson.ObjectId(id)})

    exp = {
        "id": str(e["_id"]),
        "Name": e["Name"],
        "FieldDataIDList": e["FieldDataIDList"],
        "Neglect": e["Neglect"],
        "Protected": e["Protected"],
        "FileIDList": e["FileIDList"],
        "shortId": e["ShortID"],
        "typeName": "Experiment",
    }

    exp["fields"] = getFields(exp["FieldDataIDList"], table)
    rawdata = []
    for r in RawData.objects(ExpID=bson.ObjectId(exp["id"])).order_by("Name"):
        rawdata.append({"id": str(r.id), "name": r.Name})
    exp["rawdata"] = rawdata
    exp["files"] = [
        {
            "id": str(f["_id"]),
            "Name": f["Name"],
            "Thumbnail": (
                str(f.get("ThumbnailFileID", ""))
                if f.get("ThumbnailFileID", "")
                else ""
            ),
        }
        for f in db.File.find({"_id": {"$in": exp["FileIDList"]}})
    ]

    exp["linked_items"] = []
    if get_linked:
        linked_items = get_linked_items(e["_id"])
        exp["linked_items"] = linked_items

    spreadsheet_info = get_spreadsheet_info(e["_id"], "Experiment")
    exp.update(spreadsheet_info)

    userId = flask.g.user
    exp["writable"] = Experiment.check_permission_to_project(
        e["ProjectID"], bson.ObjectId(userId), "write"
    )
    exp["admin"] = Experiment.check_permission_to_project(
        e["ProjectID"], bson.ObjectId(userId), "invite"
    )
    return exp


def prepare_mean_value_field_data(field_data_value_list):
    if field_data_value_list[0].get("type") == "Numeric":
        show_value_list = []
        original_value_list = []
        si_value_list = []
        for field_data_value in field_data_value_list:
            show_value_list.append(
                f"{field_data_value['original_value']} {field_data_value['unit']}"
            )
            original_value_list.append(field_data_value["original_value"])
            if field_data_value["si_value"] is not None:
                si_value_list.append(field_data_value["si_value"])

        unit_check = [
            fd["unit"] == field_data_value_list[0].get("unit")
            for fd in field_data_value_list
        ]
        if all(unit_check):
            mean_value = sum(original_value_list) / len(original_value_list)
            value = f"{show_value_list}, mean: {mean_value} {field_data_value_list[0].get('unit')}"
        else:
            value = f"{show_value_list}"

        if si_value_list:
            si_value_mean = sum(si_value_list) / len(si_value_list)
        else:
            si_value_mean = None

        result_dict = {
            "field_name": field_data_value_list[0]["field_name"],
            "value": value,
            "si_value": si_value_mean,
            "unit": field_data_value_list[0].get("unit"),
            "type": field_data_value_list[0]["type"],
        }
        return result_dict
    else:
        value_list = [fd["value"] for fd in field_data_value_list]
        result_dict = {
            "field_name": field_data_value_list[0]["field_name"],
            "value": f"{value_list}",
            "si_value": None,
            "unit": None,
            "type": field_data_value_list[0]["type"],
        }
        return result_dict


def get_spreadsheet_info(item_id, collection):
    returnDict = {"spreadsheet": False, "spreadsheet_template": False}
    if collection == "Experiment":
        spreadsheets = list(
            get_db().db["SpreadSheet"].find({"ExperimentIDList": {"$in": [item_id]}})
        )
        for spreadsheet in spreadsheets:
            if len(spreadsheet["ExperimentIDList"]) == 1:
                returnDict["spreadsheet"] = True
                if spreadsheet.get("Template"):
                    returnDict["spreadsheet_template"] = True
                break
    elif collection == "Sample":
        spreadsheets = list(
            get_db().db["SpreadSheet"].find({"SampleIDList": {"$in": [item_id]}})
        )
        for spreadsheet in spreadsheets:
            if len(spreadsheet["SampleIDList"]) == 1:
                returnDict["spreadsheet"] = True
                if spreadsheet.get("Template"):
                    returnDict["spreadsheet_template"] = True
                break
    elif collection == "ResearchItem":
        spreadsheets = list(
            get_db().db["SpreadSheet"].find({"ResearchItemIDList": {"$in": [item_id]}})
        )
        for spreadsheet in spreadsheets:
            if len(spreadsheet["ResearchItemIDList"]) == 1:
                returnDict["spreadsheet"] = True
                if spreadsheet.get("Template"):
                    returnDict["spreadsheet_template"] = True
                break
    else:
        return returnDict

    return returnDict


def create_thumbnail(fileDict):
    fs = FileStorage(get_db())
    size = fs.get_size(fileDict["_id"])
    if size > 100 * 1e6:
        return
    fileBytes = fs.get_file(fileDict["_id"])
    fileBytesIO = BytesIO(fileBytes)
    try:
        fileName = fileDict["Name"]
        fileroot, fileext = os.path.splitext(fileName)

        im = Image.open(fileBytesIO)
        imageSize = im.size
        imageWidth = imageSize[0]
        imageHeight = imageSize[1]
        widthToHeight = imageWidth / imageHeight
        newHeight = 150
        newWidth = newHeight * widthToHeight
        newWidth = round(newWidth)
        size = newWidth, newHeight
        im.thumbnail(size)
        thumbnailByteIO = BytesIO()
        im.save(thumbnailByteIO, "PNG")
        im.close()
        thumbnailFileID = fs.put(
            thumbnailByteIO.getbuffer().tobytes(), fileName=f"{fileroot}_thumbnail.png"
        )
        return thumbnailFileID
    except:
        return None


@bp.route("/<idStringArray>/files", methods=["POST"])
@login_required
def add_files(idStringArray: str):
    idStringArray = idStringArray.replace(" ", "")
    if "," in idStringArray:
        idList = idStringArray.split(",")
    else:
        idList = [idStringArray]
    idList = [bson.ObjectId(_id) for _id in idList]
    experiments = list(get_db().db["Experiment"].find({"_id": {"$in": idList}}))
    samples = list(get_db().db["Sample"].find({"_id": {"$in": idList}}))
    researchItems = list(get_db().db["ResearchItem"].find({"_id": {"$in": idList}}))
    itemsDict = {
        "experiments": experiments,
        "samples": samples,
        "researchitems": researchItems,
    }
    typeCollectionDict = {
        "experiments": "Experiment",
        "samples": "Sample",
        "researchitems": "ResearchItem",
    }

    userId = flask.g.user
    data = flask.request.get_json()
    fileList = []
    if "uuids" in data and all(["s3multipart-" in u for u in data["uuids"]]):
        fileList = list(get_db().db.File.find({"S3Key": {"$in": data["uuids"]}}))

    elif "uuids" in data:
        fileList = list(get_db().db.File.find({"uuid": {"$in": data["uuids"]}}))

    if fileList:
        filedata = []
        for file in fileList:
            # thumbnailID = create_thumbnail(file)
            # if thumbnailID:
            #     Update.update(Collection.File, File.ThumbnailFileID,
            #                   thumbnailID, file["_id"], get_db(), userId)
            filedata.append({"id": str(file["_id"]), "Name": file["Name"]})

            for _type in ["experiments", "samples", "researchitems"]:
                typeCollection = typeCollectionDict[_type]

                for item in itemsDict[_type]:
                    ensureAccess(typeCollection, "write", item["_id"])

                    Append.append(
                        typeCollection,
                        "FileIDList",
                        item["_id"],
                        file["_id"],
                        get_db(),
                        userId,
                    )

        return bson.json_util.dumps(filedata)
    else:
        flask.abort(400)


@bp.route("/item/<_type>/<_id>/files/<fileid>", methods=["DELETE"])
@login_required
def remove_files(_id, fileid, _type):
    from tenjin.mongo_engine import Database

    if _type.lower() == "experiments":
        collection = "Experiment"
    elif _type.lower() == "samples":
        collection = "Sample"
    else:
        collection = "ResearchItem"

    userId = flask.g.user
    cls, doc = Database.get_collection_class_and_document(collection, _id)
    doc_list, doc_access_dict = cls.check_permission([doc], "delete", userId)
    if not doc_list:
        flask.abort(400)
    Pop.pop(collection, "FileIDList", bson.ObjectId(_id), bson.ObjectId(fileid))

    return "all done"


@bp.route("/items/move", methods=["POST"])
@login_required
def move_items():
    from tenjin.mongo_engine.Group import Group

    data = flask.request.get_json()

    group_changes = []
    exp_changes = []
    sample_changes = []
    research_item_changes = []
    for d in data:
        if d["type"] == "Groups":
            group_changes.append(d)
        elif d["type"] == "Experiments":
            exp_changes.append(d)
        elif d["type"] == "Samples":
            sample_changes.append(d)
        else:
            research_item_changes.append(d)
    new_group_id = None
    if data[0]["new_group_id"]:
        new_group_id = bson.ObjectId(data[0]["new_group_id"])
    if group_changes and not new_group_id:
        group_id = bson.ObjectId(data[0]["id"])
        group_id_list, access_dict = Group.check_permission([group_id], "write")
    else:
        group_id_list, access_dict = Group.check_permission([new_group_id], "write")
    if not group_id_list:
        flask.abort(403), "no permission"

    for g_change in group_changes:
        Update.update("Group", "GroupID", new_group_id, bson.ObjectId(g_change["id"]))

    for e_change in exp_changes:
        print(bson.ObjectId(e_change["old_group_id"]))
        Append.append(
            "Experiment", "GroupIDList", bson.ObjectId(e_change["id"]), new_group_id
        )
        Pop.pop(
            "Experiment",
            "GroupIDList",
            bson.ObjectId(e_change["id"]),
            bson.ObjectId(e_change["old_group_id"]),
        )

    for s_change in sample_changes:
        Append.append(
            "Sample", "GroupIDList", bson.ObjectId(s_change["id"]), new_group_id
        )
        Pop.pop(
            "Sample",
            "GroupIDList",
            bson.ObjectId(s_change["id"]),
            bson.ObjectId(s_change["old_group_id"]),
        )

    for ri_change in research_item_changes:
        Append.append(
            "ResearchItem", "GroupIDList", bson.ObjectId(ri_change["id"]), new_group_id
        )
        Pop.pop(
            "ResearchItem",
            "GroupIDList",
            bson.ObjectId(ri_change["id"]),
            bson.ObjectId(ri_change["old_group_id"]),
        )

    return "all done"


@bp.route("/projects/<project_id>/selector_items", methods=["GET"])
@login_required
def get_items_for_selector(project_id):
    ensureAccess("Project", "read", project_id)

    project_id = bson.ObjectId(project_id)
    name = flask.request.args.get("name", None)

    exp = project_exp(project_id, name)
    samples = project_samples(project_id, name)
    researchitems = project_researchitems(project_id, name)
    total = []
    total.extend(exp)
    total.extend(samples)
    total.extend(researchitems)
    return json.dumps(total)


@bp.route("/projects/<project_id>/experiments", methods=["GET"])
@login_required
def project_exp(project_id, name=None):
    from tenjin.mongo_engine.Experiment import Experiment

    if not name:
        name = flask.request.args.get("name", None)

    if name:
        exps = (
            Experiment.objects(ProjectID=project_id, NameLower__contains=name.lower())
            .order_by("-Date")
            .only("Name", "id", "GroupIDList")
        )
    else:
        exps = (
            Experiment.objects(ProjectID=project_id)
            .order_by("Name")
            .only("Name", "id", "GroupIDList")
        )
    result = []
    category = "Last 50 experiments"
    if name:
        category = f"Experiments contain '{name}'"
    for e in exps[:50]:
        if not e["GroupIDList"]:
            continue
        result.append(
            {
                "id": str(e.id),
                "Name": e["Name"],
                "Category": "Experiment",
                "DisplayedCategory": category,
            }
        )

    return result


@bp.route("/projects/<project_id>/samples", methods=["GET"])
@login_required
def project_samples(project_id, name=None):
    from tenjin.mongo_engine.Sample import Sample

    if not name:
        name = flask.request.args.get("name", None)

    if name:
        samples = (
            Sample.objects(ProjectID=project_id, NameLower__contains=name.lower())
            .order_by("-Date")
            .only("Name", "id", "GroupIDList")
        )
    else:
        samples = (
            Sample.objects(ProjectID=project_id)
            .order_by("Name")
            .only("Name", "id", "GroupIDList")
        )

    category = "Last 50 samples"
    if name:
        category = f"Samples contain '{name}'"
    result = []
    for s in samples[:50]:
        if not s["GroupIDList"]:
            continue
        result.append(
            {
                "id": str(s.id),
                "Name": s["Name"],
                "Category": "Sample",
                "DisplayedCategory": category,
            }
        )

    return result


@bp.route("/projects/<project_id>/researchitems", methods=["GET"])
@login_required
def project_researchitems(project_id, name=None):
    from tenjin.mongo_engine import ResearchItem
    from tenjin.mongo_engine import ResearchCategory

    research_categories = ResearchCategory.objects(ProjectID=project_id).only(
        "Name", "id"
    )
    research_categories_mapping = {rg.id: rg["Name"] for rg in research_categories}
    result = []

    if not name:
        name = flask.request.args.get("name", None)

    result = []
    for rg_id in research_categories_mapping:
        if name:
            research_items = (
                ResearchItem.objects(
                    NameLower__contains=name.lower(), ResearchCategoryID=rg_id
                )
                .order_by("-Date")
                .only("Name", "id", "GroupIDList")
            )
        else:
            research_items = (
                ResearchItem.objects(ResearchCategoryID=rg_id)
                .order_by("Name")
                .only("Name", "id", "GroupIDList")
            )
        cat_name = research_categories_mapping[rg_id]
        category = f"Last 50 {cat_name}"
        if name:
            category = f"{cat_name} contain '{name}')"

        for ri in research_items[:50]:
            if not ri["GroupIDList"]:
                continue
            result.append(
                {
                    "id": str(ri.id),
                    "Name": ri["Name"],
                    "Category": cat_name,
                    "DisplayedCategory": category,
                }
            )

    return result


def get_linked_items(item_id):
    from tenjin.mongo_engine.Link import Link
    from tenjin.mongo_engine.Experiment import Experiment
    from tenjin.mongo_engine.Sample import Sample
    from tenjin.mongo_engine.ResearchItem import ResearchItem
    from tenjin.mongo_engine.ResearchCategory import ResearchCategory

    links = Link.objects(Q(DataID1=item_id) | Q(DataID2=item_id))
    sample_id_list = []
    exp_id_list = []
    item_id_list = []
    for link in links:
        if link.DataID1 == item_id:
            if link.Collection2 == "Sample":
                sample_id_list.append(link.DataID2)
            elif link.Collection2 == "Experiment":
                exp_id_list.append(link.DataID2)
            else:
                item_id_list.append(link.DataID2)
        elif link.DataID2 == item_id:
            if link.Collection1 == "Sample":
                sample_id_list.append(link.DataID1)
            elif link.Collection1 == "Experiment":
                exp_id_list.append(link.DataID1)
            else:
                item_id_list.append(link.DataID1)

    linked_items = []

    linked_items.extend(
        {
            "id": str(s.id),
            "Name": s.Name,
            "Category": "Sample",
            "DisplayedCategory": "Linked samples",
        }
        for s in Sample.objects(id__in=sample_id_list)
    )

    linked_items.extend(
        {
            "id": str(exp.id),
            "Name": exp.Name,
            "Category": "Experiment",
            "DisplayedCategory": "Linked experiments",
        }
        for exp in Experiment.objects(id__in=exp_id_list)
    )

    research_items = ResearchItem.objects(id__in=item_id_list)
    research_categories_id_list = [
        research_item.ResearchCategoryID.id for research_item in research_items
    ]
    research_categories = ResearchCategory.objects(id__in=research_categories_id_list)
    research_category_mapping = {
        research_category.id: research_category.Name
        for research_category in research_categories
    }
    research_items_new = []
    for research_item in research_items:
        if research_item.ResearchCategoryID.id not in research_category_mapping:
            continue
        category = research_category_mapping[research_item.ResearchCategoryID.id]
        research_items_new.append(
            {
                "id": str(research_item.id),
                "Name": research_item[ResearchItem.Name.name],
                "Category": category,
                "DisplayedCategory": f"Linked {category}",
            }
        )
    research_items_new.sort(key=operator.itemgetter("Category", "Name"))
    linked_items.extend(research_items_new)

    return linked_items


def get_item_for_dashboard(project_id, item_id_list):
    from tenjin.mongo_engine.Experiment import Experiment
    from tenjin.mongo_engine.Sample import Sample
    from tenjin.mongo_engine.ResearchItem import ResearchItem

    project_id = bson.ObjectId(project_id)
    item_id_list = [bson.ObjectId(i) for i in item_id_list]
    items = []
    import time

    experiments = list(
        get_db()
        .db["Experiment"]
        .find(
            {"_id": {"$in": item_id_list}},
            {"_id": 1, "Name": 1, "NameLower": 1, "ShortID": 1, "FieldDataIDList": 1},
        )
    )
    # experiments, _ = Experiment.check_permission(experiments, "read")
    for e in experiments:
        e.update({"type": "Experiments"})
        items.append(e)
    samples = list(
        get_db()
        .db["Sample"]
        .find(
            {"_id": {"$in": item_id_list}},
            {"_id": 1, "Name": 1, "NameLower": 1, "ShortID": 1, "FieldDataIDList": 1},
        )
    )
    # samples, _ = Sample.check_permission(samples, "read")
    for s in samples:
        s.update({"type": "Samples"})
        items.append(s)

    researchitems = list(
        get_db()
        .db["ResearchItem"]
        .find(
            {"_id": {"$in": item_id_list}},
            {
                "_id": 1,
                "Name": 1,
                "NameLower": 1,
                "ShortID": 1,
                "ResearchCategoryID": 1,
                "FieldDataIDList": 1,
            },
        )
    )
    # researchitems, _ = ResearchItem.check_permission(researchitems, "read")

    categories = (
        get_db()
        .db["ResearchCategory"]
        .find({"ProjectID": project_id}, {"_id": 1, "Name": 1})
        .sort("Name")
    )
    category_mapping = {c["_id"]: c["Name"] for c in categories}
    for ri in researchitems:
        ri["type"] = category_mapping[ri["ResearchCategoryID"]]
        items.append(ri)

    sorted_items = sorted(items, key=lambda x: x["NameLower"])
    result = []
    for item in sorted_items:
        result.append(
            {
                "id": str(item["_id"]),
                "name": item["Name"],
                "type": item["type"],
                "short_id": item["ShortID"],
                "field_data_id_list": [str(f) for f in item["FieldDataIDList"]],
            }
        )
    return result

