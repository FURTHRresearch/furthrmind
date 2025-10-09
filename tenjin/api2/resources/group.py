import asyncio
import bson
import flask
from webargs.flaskparser import use_args

from tenjin.database.db import get_db

from tenjin.api2.schema.group_schema import GroupSchema, GroupPostSchema

from tenjin.mongo_engine.Group import Group
from tenjin.mongo_engine.File import File

from tenjin.execution.update import Update
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete
from tenjin.web.helper.filterHelper_bak2 import get_linked_items_recursive

from .helper_methods import (get_inner_data, 
                             get_id_list_from_request_and_check_permission, 
                             response_wrapper,
                             get_json_from_request,
                             prepare_fielddata_query_input)

from tenjin.api2.resources.fielddata import get_fielddata_method, update_or_create_fielddata_method
from tenjin.api2.schema.query_input_schema import QueryInputSchema
from tenjin.api2.schema.get_all_standard_schema import GetAllStandardSchema

from tenjin.web.helper.filter_utils import get_groups

bp = flask.Blueprint('api2/group', __name__)

def get_many_group(group_id_list: list[bson.ObjectId], project_id: bson.ObjectId) -> list[dict]:
    result = []
    db = get_db().db

    cursor = db["Group"].find({"_id": {"$in": group_id_list}})

    fieldDataList = get_fielddata_method(project_id, cursor.distinct("FieldDataIDList"))
    fieldDataDict = {f["_id"]: f for f in fieldDataList}

    expCursor = db["Experiment"].find({"GroupIDList": {"$in": group_id_list}},
                                               {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1})
    sampleCursor = db["Sample"].find({"GroupIDList": {"$in": group_id_list}},
                                              {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1})

    research_items = list(db["ResearchItem"].find({"GroupIDList": {"$in": group_id_list}},
                                                           {"_id": 1, "GroupIDList": 1, "Name": 1,
                                                            "ShortID": 1, "ResearchCategoryID": 1}))
    category_id_list = [r["ResearchCategoryID"] for r in research_items]
    research_categories = list(db["ResearchCategory"].find({"_id": {"$in": category_id_list}},
                                                                    {"_id": 1, "ProjectID": 1, "Name": 1}))
    category_mapping = {c["_id"]: c for c in research_categories}

    def prepare_Sample_Exp_Dict(_cursor):
        item_dict = {}
        for item in _cursor:
            for groupID in item.get("GroupIDList", []):
                if groupID in item_dict:
                    item_dict[groupID].append(item)
                    # item_dict[groupID].append({"id": str(item.get("_id")), "name": item.get("Name")})
                else:
                    item_dict[groupID] = [item]
                    # item_dict[groupID] = [{"id": str(item.get("_id")), "name": item.get("Name")}]
        return item_dict

    expDict = prepare_Sample_Exp_Dict(expCursor)
    sampleDict = prepare_Sample_Exp_Dict(sampleCursor)

    def prepare_research_item_dict(research_items):
        item_dict = {}
        for item in research_items:
            cat_id = item["ResearchCategoryID"]
            cat_name = category_mapping[cat_id]["Name"]
            for groupID in item.get("GroupIDList", []):
                if groupID not in item_dict:
                    item_dict[groupID] = {}
                if cat_name not in item_dict[groupID]:
                    item_dict[groupID][cat_name] = []
                item_dict[groupID][cat_name].append(item)
        return item_dict

    researchItemDict = prepare_research_item_dict(research_items)

    subgroups = Group.objects(GroupID__in=group_id_list).only("id", "Name", "GroupID")
    subgroup_mapping = {}
    for subgroup in subgroups:
        if subgroup.GroupID.id not in subgroup_mapping:
            subgroup_mapping[subgroup.GroupID.id] = []
        subgroup_mapping[subgroup.GroupID.id].append(subgroup)

    parent_id_list = []
    groups = cursor.to_list()
    for group in groups:
        if group["GroupID"]:
            parent_id_list.append(group["GroupID"])
    parent_groups = Group.objects(id__in=parent_id_list).only("id", "Name")
    parent_groups_mapping = {p.id: p for p in parent_groups}

    for group in groups:
        result.append({
            "id": str(group.get("_id")),
            "name": group.get("Name"),
            "shortid": group.get("ShortID"),
            "fielddata": [fieldDataDict.get(fieldDataID) for fieldDataID in group.get("FieldDataIDList")],
            "experiments": expDict.get(group.get("_id"), []),
            "samples": sampleDict.get(group.get("_id"), []),
            "researchitems": researchItemDict.get(group.get("_id"), {}),
            "sub_groups": subgroup_mapping.get(group.get("_id"), []),
            "parent_group": parent_groups_mapping.get(group.get("GroupID"))
        })

    return result

@bp.route('/<project_id>/group/<group_id>', methods=['GET'])
@bp.route('/<project_id>/groups/<group_id>', methods=['GET'])
@response_wrapper
def get(project_id: str, group_id: str):
    """
    Get a group by ID
    ---
    """
    from mongo_engine.Project import Project
    from mongo_engine.Group import Group
    
    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        PermissionError("You do not have permission to access this project.")
    
    group_id = bson.ObjectId(group_id)
    group = Group.objects(id=group_id, ProjectID=project_id).only("id").first()
    if not group:
        raise ValueError("Group not found.")
    
    result = get_many_group([group_id], project_id)
    result = result[0]
    dumped_result = GroupSchema().dump(result)
    return dumped_result

@bp.route('/<project_id>/groups', methods=['GET'])
@bp.route('/<project_id>/group', methods=['GET']) 
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_all(args, project_id: str):
    """
    Get all groups
    ---
    """
    from mongo_engine.Group import Group
    from mongo_engine.Project import Project
    
    project_id = bson.ObjectId(project_id)

    if args:
        id_list = get_id_list_from_request_and_check_permission("Group", args, "read", project_id=project_id)
        
        if "fielddata" not in args:
            results = get_many_group(id_list, project_id)
            dumped = GroupSchema().dump(results, many=True)
        
        elif "fielddata" in args:
            fielddata_query_dict = prepare_fielddata_query_input(args["fielddata"], project_id)
            combo_filter = fielddata_query_dict.get("combo")
            numeric_filter = fielddata_query_dict.get("numeric")
            checks_filter = fielddata_query_dict.get("checkbox")
            date_filter = fielddata_query_dict.get("date")
            text_filter = fielddata_query_dict.get("singleline")
            
            group_id_list = []
            async def _get_groups_async():
                coroutines = [get_groups(
                    project_id, id_list, 
                    group_filter=None,
                    name_filter=None,
                    combo_filter=combo_filter,
                    numeric_filter=numeric_filter,
                    checks_filter=checks_filter,
                    date_filter=date_filter,
                    text_filter=text_filter
                )]
                result = await asyncio.gather(*coroutines)
                group_id_list.extend(result[0])

            asyncio.run(_get_groups_async())
            groups = Group.objects(id__in=group_id_list).only("id", "Name", "ShortID")
            dumped = GetAllStandardSchema().dump(list(groups), many=True)
            
    else:
        access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
        if not access:
            PermissionError("You do not have permission to access this project.")
        groups = Group.objects(ProjectID=project_id).only("id", "Name", "ShortID")
        dumped = GetAllStandardSchema().dump(list(groups), many=True)
    
    return dumped

@bp.route('/<project_id>/groups', methods=['POST'])
@bp.route('/<project_id>/group', methods=['POST']) 
@response_wrapper
def post(project_id: str):

    from mongo_engine.Project import Project
    from mongo_engine.Group import Group

    data_list = get_json_from_request()
    data_list = GroupPostSchema().load(data_list, many=True)
    
    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="write")
    return_id_list = []
    
    if not access:
        PermissionError("You do not have permission to create or update a group in this project.")
    for data in data_list:
        if "ShortID" in data:
            group = Group.objects(ShortID=data["ShortID"], ProjectID=project_id).only("id").first()
            if group:
                data["_id"] = group.id
            data.pop("ShortID")
            
        if "_id" not in data:
            assert "Name" in data, "Group name is required."
            data["ProjectID"] = project_id
            param = {"ProjectID": project_id, "Name": data["Name"]}
            group_id = Create.create("Group", param)
            data.pop("Name")
            data["_id"] = group_id
            
            
        if "_id" in data:
            group_id = bson.ObjectId(data.pop("_id"))
            group = Group.objects(id=group_id, ProjectID=project_id).first()
            if not group:
                raise ValueError("Group not found.")
            
            direct_update_keys = ["Name", "GroupID"]
            for key in data:
                if key in direct_update_keys:
                    Update.update("Group", key, data["key"], group_id)
                elif key == "files":
                    # To ensure, that all files exist
                    file_id_list = [f["_id"] for f in data["files"]]
                    files = File.objects(id__in=file_id_list).only("id")
                    existing_file_id_list = [f.id for f in files]
                    file_id_list = [f_id for f_id in file_id_list if f_id in existing_file_id_list]
                    Update.update("Group", "FileIDList", file_id_list, group_id)
                elif key == "fielddata":
                    fielddata_arg_list = data["fielddata"]
                    fielddata_id_list = []
                    for fielddata_arg in fielddata_arg_list:
                        fielddata_id = update_or_create_fielddata_method(fielddata_arg, project_id)
                        fielddata_id_list.append(fielddata_id)
                    Update.update("Group", "FieldDataIDList", fielddata_id_list, group_id)
        
        return_id_list.append(group_id)
                    
    return return_id_list

@bp.route('/<project_id>/groups/<group_id>', methods=['DELETE'])
@bp.route('/<project_id>/group/<group_id>', methods=['DELETE'])
@response_wrapper
def delete(project_id: str, group_id: str):
    """
    Delete a group by ID
    ---
    """
    from mongo_engine.Project import Project
    from mongo_engine.Group import Group
    
    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="delete")
    if not access:
        PermissionError("You do not have permission to delete this group.")
    
    group_id = bson.ObjectId(group_id)
    group = Group.objects(id=group_id, ProjectID=project_id).first()
    if not group:
        raise ValueError("Group not found.")
    
    Delete.delete("Group", group_id)
    
    return group_id