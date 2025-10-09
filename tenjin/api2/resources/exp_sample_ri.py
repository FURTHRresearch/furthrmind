import bson
import flask
import asyncio
from webargs.flaskparser import use_args
from mongoengine import Q

from tenjin.database.db import get_db
from tenjin.mongo_engine import Database
from tenjin.web.helper.filter_utils import filter_items

from tenjin.api2.schema.exp_sample_ri_schema import ExpSampleRiSchema, ExpSampleRiPostSchema

from tenjin.api2.resources.datatable import update_or_create_datatable_method

from tenjin.execution.update import Update
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete

from .helper_methods import (
    get_inner_data,
    get_id_list_from_request_and_check_permission,
    response_wrapper,
    get_json_from_request,
    get_linked_items,
    prepare_fielddata_query_input,
    write_links
)
from tenjin.api2.resources.fielddata import (
    get_fielddata_method,
    update_or_create_fielddata_method,
)
from tenjin.api2.schema.query_input_schema import QueryInputSchema
from tenjin.api2.schema.get_all_standard_schema import GetAllStandardSchema

from tenjin.mongo_engine.RawData import RawData
from tenjin.mongo_engine.Column import Column
from tenjin.mongo_engine.Sample import Sample
from tenjin.mongo_engine.Experiment import Experiment
from tenjin.mongo_engine.ResearchItem import ResearchItem
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.ResearchCategory import ResearchCategory

bp = flask.Blueprint("api2/exp_sample_ri", __name__)


def get_many_items(
    item_id_list: list[bson.ObjectId], collection_string: str, project_id: bson.ObjectId
) -> list[dict]:

    db = get_db().db

    links = get_linked_items(item_id_list)
    linked_exp_id_list = links[0]
    linked_sample_id_list = links[1]
    linked_researchitem_id_list = links[2]
    linked_expId_expId_mapping = links[3]
    linked_expId_sampleId_mapping = links[4]
    linked_expId_researchitemId_mapping = links[5]
    
    linked_exps = Experiment.objects(id__in=linked_exp_id_list).only(
        "id", "Name", "ShortID"
    )
    linked_exp_dict = {exp.id: exp.to_mongo() for exp in linked_exps}

    linked_samples = Sample.objects(id__in=linked_sample_id_list).only(
        "id", "Name", "ShortID"
    )
    linked_sample_dict = {sample.id: sample.to_mongo() for sample in linked_samples}

    cursor = db[collection_string].find({"_id": {"$in": item_id_list}})
    fileDict = get_inner_data("File", cursor.distinct("FileIDList"))
    groupDict = get_inner_data("Group", cursor.distinct("GroupIDList"))
    fieldDataList = get_fielddata_method(project_id, cursor.distinct("FieldDataIDList"))
    fieldDataDict = {f["_id"]: f for f in fieldDataList}

    research_items = ResearchItem.objects(id__in=linked_researchitem_id_list).only(
        "id", "Name", "ShortID", "ResearchCategoryID"
    )
    research_item_mapping = {r.id: r for r in research_items}

    category_id_list = [r.ResearchCategoryID.id for r in research_items]
    research_categories = list(
        db["ResearchCategory"].find({"ProjectID": project_id}, {"_id": 1, "Name": 1})
    )
    category_mapping = {c["_id"]: c for c in research_categories}
    exp_research_item_mapping = {}
    item_list = list(cursor)
    for item in item_list:
        item_id = item["_id"]
        if item_id not in linked_expId_researchitemId_mapping:
            continue

        for r_id in linked_expId_researchitemId_mapping[item_id]:
            item = research_item_mapping[r_id]
            cat_id = item.ResearchCategoryID.id
            cat_name = category_mapping[cat_id].get("Name")
            if item_id not in exp_research_item_mapping:
                exp_research_item_mapping[item_id] = {}
            if cat_name not in exp_research_item_mapping[item_id]:
                exp_research_item_mapping[item_id][cat_name] = []
            exp_research_item_mapping[item_id][cat_name].append(item.to_mongo())

    query = Q(ExpID__in=item_id_list) | Q(SampleID__in=item_id_list) | Q(ResearchItemID__in=item_id_list)
    raw_data_query = RawData.objects(query).only(
        "id", "Name", "ColumnIDList", "ExpID", "SampleID", "ResearchItemID"
    )
    column_id_list = []
    for raw_data in raw_data_query:
        column_id_list.extend([c.id for c in raw_data.ColumnIDList])

    columns = Column.objects(id__in=column_id_list).only("id", "Name")
    column_mapping = {c.id: c.to_mongo() for c in columns}

    rawDataDict = {}
    for rawData in raw_data_query:
        if rawData.ExpID:
            item_id = rawData.ExpID.id
        elif rawData.SampleID:
            item_id = rawData.SampleID.id
        elif rawData.ResearchItemID:
            item_id = rawData.ResearchItemID.id
        else:
            continue
        raw_data = rawData.to_mongo()
        raw_data["columns"] = [
            column_mapping[c.id] for c in rawData.ColumnIDList if c.id in column_mapping
        ]

        if item_id in rawDataDict:
            rawDataDict[item_id].append(raw_data)
        else:
            rawDataDict[item_id] = [raw_data]

    results = []
    for item in item_list:
        results.append(
            {
                "id": str(item.get("_id")),
                "name": item.get("Name"),
                "neglect": item.get("Neglect"),
                "shortid": item.get("ShortID"),
                "files": [
                    fileDict.get(fileID) for fileID in item.get("FileIDList")
                ],
                "fielddata": [
                    fieldDataDict.get(fieldDataID)
                    for fieldDataID in item.get("FieldDataIDList")
                ],
                "linked_experiments": [
                    linked_exp_dict.get(exp_id)
                    for exp_id in linked_expId_expId_mapping.get(
                        item.get("_id"), []
                    )
                ],
                "linked_samples": [
                    linked_sample_dict.get(sampleID)
                    for sampleID in linked_expId_sampleId_mapping.get(
                        item.get("_id"), []
                    )
                ],
                "groups": [
                    groupDict.get(groupID) for groupID in item.get("GroupIDList")
                ],
                "linked_researchitems": exp_research_item_mapping.get(
                    item.get("_id"), {}
                ),
                "category": category_mapping.get(item.get("ResearchCategoryID")),
                "datatables": rawDataDict.get(item.get("_id"), []),
                "protected": item.get("Protected", False),
            }
        )

    return results


@bp.route("/<project_id>/experiment/<item_id>", methods=["GET"])
@bp.route("/<project_id>/experiments/<item_id>", methods=["GET"])
@bp.route("/<project_id>/sample/<item_id>", methods=["GET"])
@bp.route("/<project_id>/samples/<item_id>", methods=["GET"])
@bp.route("/<project_id>/researchitem/<item_id>", methods=["GET"])
@bp.route("/<project_id>/researchitems/<item_id>", methods=["GET"])
@response_wrapper
def get(project_id: str, item_id: str):
    """
    Get an experiment by ID
    ---
    """
    
    path = flask.request.path
    path_splitted = path.split("/")
    collection_string = path_splitted[-2]
    if "experiment" in collection_string:
        collection_string = "Experiment"
    elif "sample" in collection_string:
        collection_string = "Sample"
    elif "researchitem" in collection_string:
        collection_string = "ResearchItem"
    else:
        raise ValueError("Invalid collection in URL.")

    collection_class = Database.get_collection_class(collection_string)

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        PermissionError("You do not have permission to access this project.")

    item_id = bson.ObjectId(item_id)
    item = collection_class.objects(id=item_id, ProjectID=project_id).only("id").first()
    if not item:
        raise ValueError("Item not found.")

    result = get_many_items([item_id], collection_string, project_id)
    result = result[0]
    dumped_result = ExpSampleRiSchema().dump(result)
    return dumped_result


@bp.route("/<project_id>/experiment", methods=["GET"])
@bp.route("/<project_id>/experiments", methods=["GET"])
@bp.route("/<project_id>/sample", methods=["GET"])
@bp.route("/<project_id>/samples", methods=["GET"])
@bp.route("/<project_id>/researchitem", methods=["GET"])
@bp.route("/<project_id>/researchitems", methods=["GET"])
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_all(args, project_id: str):
    """
    Get all experiments, optionally filtered by query parameters
    ---
    """
    from mongo_engine.Experiment import Experiment
    from mongo_engine.Project import Project

    project_id = bson.ObjectId(project_id)

    path = flask.request.path
    path_splitted = path.split("/")
    collection_string = path_splitted[-1]
    if "experiment" in collection_string:
        collection_string = "Experiment"
    elif "sample" in collection_string:
        collection_string = "Sample"
    elif "researchitem" in collection_string:
        collection_string = "ResearchItem"
    else:
        raise ValueError("Invalid collection in URL.")
    
    collection_class = Database.get_collection_class(collection_string)
    
    if args:
        id_list = get_id_list_from_request_and_check_permission(
            collection_string, args, "read", project_id=project_id
        )
        if "fielddata" not in args:
            results = get_many_items(id_list, collection_string, project_id)
            dumped = ExpSampleRiSchema().dump(results, many=True)

        elif "fielddata" in args:
            fielddata_query_dict = prepare_fielddata_query_input(
                args["fielddata"], project_id
            )
            combo_filter = fielddata_query_dict.get("combo")
            numeric_filter = fielddata_query_dict.get("numeric")
            checks_filter = fielddata_query_dict.get("checkbox")
            date_filter = fielddata_query_dict.get("date")
            text_filter = fielddata_query_dict.get("singleline")
            include_linked = 0
            if "include_linked" in args:
                include_linked = args["include_linked"]
                try:
                    include_linked = int(include_linked)
                except:
                    raise ValueError("include_linked must be an integer.")

            item_id_list = []

            async def _get_items_async():
                coroutines = [
                    filter_items(
                        project_id,
                        id_list,
                        sample_ids=[],
                        research_item_ids=[],
                        experiment_filter=None,
                        sample_filter=None,
                        research_item_filter=None,
                        date_created=None,
                        name_filter=None,
                        combo_filter=combo_filter,
                        numeric_filter=numeric_filter,
                        checks_filter=checks_filter,
                        date_filter=date_filter,
                        text_filter=text_filter,
                        include_linked=include_linked,
                    )
                ]
                result = await asyncio.gather(*coroutines)
                item_id_list.extend(result[0])

            asyncio.run(_get_items_async())
            items = collection_class.objects(id__in=item_id_list).only("id", "Name", "ShortID")
            dumped = GetAllStandardSchema().dump(list(items), many=True)

    else:
        access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
        if not access:
            raise PermissionError(
                "You do not have permission to read columns in this project."
            )
        exps = collection_class.objects(ProjectID=project_id).only("id", "Name", "ShortID")
        dumped = GetAllStandardSchema().dump(list(exps), many=True)

    return dumped


@bp.route("/<project_id>/experiment", methods=["POST"])
@bp.route("/<project_id>/experiments", methods=["POST"])
@bp.route("/<project_id>/sample", methods=["POST"])
@bp.route("/<project_id>/samples", methods=["POST"])
@bp.route("/<project_id>/researchitem", methods=["POST"])
@bp.route("/<project_id>/researchitems", methods=["POST"])
@response_wrapper
def post(project_id: str):

    data_list = get_json_from_request()
    data_list = ExpSampleRiPostSchema().load(data_list, many=True)

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="write")
    
    path = flask.request.path
    path_splitted = path.split("/")
    collection_string = path_splitted[-1]
    if "experiment" in collection_string:
        collection_string = "Experiment"
    elif "sample" in collection_string:
        collection_string = "Sample"
    elif "researchitem" in collection_string:
        collection_string = "ResearchItem"
    else:
        raise ValueError("Invalid collection in URL.")
    
    collection_class = Database.get_collection_class(collection_string)
    
    return_id_list = []

    if not access:
        PermissionError(
            "You do not have permission to create or update a group in this project."
        )
    for data in data_list:
        if "_id" not in data:
            if "Name" not in data:
                raise ValueError(f"{collection_string} name is required.")
            if "groups" not in data:
                raise ValueError("groups is required.")
            group_id_list = [g["_id"] for g in data["groups"]]
            param = {
                "ProjectID": project_id,
                "Name": data["Name"],
                "GroupIDList": group_id_list,
            }
            
            if collection_string == "ResearchItem":
                if "category" not in data:
                    raise ValueError("category is required for researchitems.")
                if "_id" in data["category"]:
                    cat_id = data["category"]["_id"]
                    cat = ResearchCategory.objects(id=cat_id, ProjectID=project_id).only("id").first()
                    if not cat:
                        raise ValueError("Research category not found.")
                    param["ResearchCategoryID"] = cat_id
                
                elif "Name" in data["category"]:
                    cat = ResearchCategory.objects(
                        Name=data["category"]["Name"], ProjectID=project_id
                    ).only("id").first()
                    if not cat:
                        raise ValueError("Research category not found.")
                    param["ResearchCategoryID"] = cat.id
                else:
                    raise ValueError("category must have either id or name.")
            
            item_id = Create.create(collection_string, param)
            data.pop("Name")
            data.pop("groups")
            data["_id"] = item_id

        if "_id" in data:
            item_id = bson.ObjectId(data.pop("_id"))
            item = collection_class.objects(id=item_id, ProjectID=project_id).first()
            if not item:
                raise ValueError(f"{collection_string} not found.")

            direct_update_keys = ["Name", "Neglect", "Protected"]
            for key in data:
                if key in direct_update_keys:
                    Update.update(collection_string, key, data[key], item_id)
                elif key == "files":
                    file_id_list = [f["_id"] for f in data["files"]]
                    Update.update(collection_string, "FileIDList", file_id_list, item_id)
                elif key == "fielddata":
                    fielddata_arg_list = data["fielddata"]
                    fielddata_id_list = []
                    for fielddata_arg in fielddata_arg_list:
                        fielddata_id = update_or_create_fielddata_method(
                            fielddata_arg, project_id
                        )
                        fielddata_id_list.append(fielddata_id)
                    Update.update(
                        collection_string, "FieldDataIDList", fielddata_id_list, item_id
                    )
                elif key == "groups":
                    group_id_list = [g["_id"] for g in data["groups"]]
                    Update.update(collection_string, "GroupIDList", group_id_list, item_id)
                elif key == "datatables" or key == "rawdata":
                    for dt in data[key]:
                        if collection_string == "Experiment" and "exp" not in dt:
                            dt["exp"] = {"_id": item_id}
                            if "sample" in dt:
                                dt.pop("sample")
                            if "researchitem" in dt:
                                dt.pop("researchitem")
                        elif collection_string == "Sample" and "sample" not in dt:
                            dt["sample"] = {"_id": item_id}
                            if "exp" in dt:
                                dt.pop("exp")
                            if "researchitem" in dt:
                                dt.pop("researchitem")
                        elif collection_string == "ResearchItem" and "researchitem" not in dt:
                            dt["researchitem"] = {"_id": item_id}
                            if "exp" in dt:
                                dt.pop("exp")
                            if "sample" in dt:
                                dt.pop("sample")
 
                        dt_id = update_or_create_datatable_method(dt, project_id)
                        
                elif key == "experiments" or key == "samples" or key == "researchitems":
                    linked_collection = None
                    if key == "experiments":
                        linked_collection = "Experiment"
                    elif key == "samples":
                        linked_collection = "Sample"
                    elif key == "researchitems":
                        linked_collection = "ResearchItem"
                    item_id_list = []
                    for item in data[key]:
                        if "_id" not in item:
                            raise ValueError("Linked items must have an id.")
                        item_id_list.append(item["_id"])
                    write_links(item_id, collection_string, item_id_list, linked_collection)

        return_id_list.append(item_id)

    return return_id_list


@bp.route("/<project_id>/experiment/<item_id>", methods=["DELETE"])
@bp.route("/<project_id>/experiments/<item_id>", methods=["DELETE"])
@bp.route("/<project_id>/sample/<item_id>", methods=["DELETE"])
@bp.route("/<project_id>/samples/<item_id>", methods=["DELETE"])
@bp.route("/<project_id>/researchitem/<item_id>", methods=["DELETE"])
@bp.route("/<project_id>/researchitems/<item_id>", methods=["DELETE"])
@response_wrapper
def delete(project_id: str, item_id: str):
    """
    Delete a experiment by ID
    ---
    """

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(
        project_id, flask.g.user, flag="delete"
    )
    if not access:
        PermissionError("You do not have permission to delete this experiment.")

    path = flask.request.path
    path_splitted = path.split("/")
    collection_string = path_splitted[-2]
    if "experiment" in collection_string:
        collection_string = "Experiment"
    elif "sample" in collection_string:
        collection_string = "Sample"
    elif "researchitem" in collection_string:
        collection_string = "ResearchItem"
    else:
        raise ValueError("Invalid collection in URL.")
    
    collection_class = Database.get_collection_class(collection_string)

    item_id = bson.ObjectId(item_id)
    item = collection_class.objects(id=item_id, ProjectID=project_id).first()
    if not item:
        raise ValueError(f"{collection_string} not found.")

    Delete.delete(collection_string, item_id)

    return item_id
