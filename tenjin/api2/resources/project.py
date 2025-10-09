from tenjin.database.db import get_db
import bson
from tenjin.api2.schema.project_schema import ProjectSchema, ProjectPostSchema, ProjectAllSchema
from tenjin.api2.schema.response_schema import ResponseSchemaListValueStr, ResponseSchema, Response
from tenjin.execution.update import Update
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete

import flask
from .helper_methods import (get_id_list_from_request_and_check_permission,
                             get_json_from_request)
from tenjin.api2.schema.query_input_schema import QueryInputSchema, IdInputSchema
from webargs.flaskparser import use_args
from .helper_methods import response_wrapper




bp = flask.Blueprint('api2/project', __name__)



def get_many_projects(project_id_list: list[bson.ObjectId]):
    from tenjin.mongo_engine.Permission import Permission
    from tenjin.mongo_engine.User import User
    from tenjin.mongo_engine.UserGroup import UserGroup
    from tenjin.mongo_engine.Project import Project
    mongoClient = get_db().db
    result = []

    project_list = list(mongoClient["Project"].find({"_id": {"$in": project_id_list}}))

    unitDict = {}
    fieldDict = {}

    unitCursor = mongoClient["Unit"].find({"$or": [{"ProjectID": {"$in": project_id_list}}, {"Predefined": True}]})
    for unit in unitCursor:
        project = unit.get("ProjectID")
        if unit.get("Predefined"):
            projects = project_id_list
        else:
            projects = [project]

        for projectID in projects:
            if projectID in unitDict:
                unitDict[projectID].append(unit)
            else:
                unitDict[projectID] = [unit]

    field_list = list(mongoClient["Field"].find({"ProjectID": {"$in": project_id_list}},
                                                {"_id": 1, "ProjectID": 1, "Name": 1, "Type": 1}))
    field_id_list = [f["_id"] for f in field_list]
    combo_entry_list = list(mongoClient["ComboBoxEntry"].find({"FieldID": {"$in": field_id_list}},
                                                            {"_id": 1, "FieldID": 1, "Name": 1}))
    field_combo_mapping = {}
    for c in combo_entry_list:
        if c["FieldID"]:
            field_id = c["FieldID"]
            if field_id not in field_combo_mapping:
                field_combo_mapping[field_id] = []
            c.pop("FieldID")
            field_combo_mapping[field_id].append(c)
    for field in field_list:
        field["comboboxentries"] = []
        if field["_id"] in field_combo_mapping:
            field["comboboxentries"] = field_combo_mapping[field["_id"]]
        projectID = field.get("ProjectID")
        if projectID in fieldDict:
            fieldDict[projectID].append(field)
        else:
            fieldDict[projectID] = [field]

    groups = list(mongoClient["Group"].find({"ProjectID": {"$in": project_id_list}},
                                            {"_id": 1, "ProjectID": 1, "Name": 1, "ShortID": 1}))
    groupIDList = [g["_id"] for g in groups]
    samples = list(mongoClient["Sample"].find({"GroupIDList": {"$in": groupIDList}},
                                            {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1}))
    exps = list(mongoClient["Experiment"].find({"GroupIDList": {"$in": groupIDList}},
                                            {"_id": 1, "GroupIDList": 1, "Name": 1, "ShortID": 1}))
    research_categories = list(mongoClient["ResearchCategory"].find({"ProjectID": {"$in": project_id_list}},
                                                                    {"_id": 1, "ProjectID": 1, "Name": 1}))
    category_mapping = {c["_id"]: c for c in research_categories}
    research_items = list(mongoClient["ResearchItem"].find({"GroupIDList": {"$in": groupIDList}},
                                                        {"_id": 1, "GroupIDList": 1, "Name": 1,
                                                            "ResearchCategoryID": 1}))

    owner_id_list = [pro["OwnerID"] for pro in project_list]
    users_owner = User.objects(id__in=owner_id_list)
    users_owner_mapping = {u.id: {"id": u.id, "email": u.Email} for u in users_owner}

    permissions = list(Permission.objects(ProjectID__in=project_id_list))
    permission_mapping = {p.id: p for p in permissions}
    permission_id_list = [p.id for p in permissions]

    users_permissions = User.objects(PermissionIDList__in=permission_id_list)
    user_groups = UserGroup.objects(PermissionIDList__in=permission_id_list)

    group_id_project_id_mapping = {}
    project_group_mapping = {}
    project_exp_mapping = {}
    project_sample_mapping = {}
    project_category_mapping = {}
    project_user_mapping = {}
    project_user_group_mapping = {}

    for group in groups:
        project_id = group["ProjectID"]
        group_id_project_id_mapping[group["_id"]] = project_id
        if project_id not in project_group_mapping:
            project_group_mapping[project_id] = [group]
        else:
            project_group_mapping[project_id].append(group)

    for exp in exps:
        group_id = exp["GroupIDList"][0]
        project_id = group_id_project_id_mapping[group_id]
        if project_id not in project_exp_mapping:
            project_exp_mapping[project_id] = [exp]
        else:
            project_exp_mapping[project_id].append(exp)

    for sample in samples:
        group_id = sample["GroupIDList"][0]
        project_id = group_id_project_id_mapping[group_id]
        if project_id not in project_sample_mapping:
            project_sample_mapping[project_id] = [sample]
        else:
            project_sample_mapping[project_id].append(sample)

    for r in research_items:
        category = category_mapping.get(r["ResearchCategoryID"])
        if not category:
            continue
        project_id = category["ProjectID"]
        if project_id not in project_category_mapping:
            project_category_mapping[project_id] = {}
        temp_dict = project_category_mapping[project_id]
        cat_name = category["Name"]
        if cat_name not in temp_dict:
            temp_dict[cat_name] = []
        temp_dict[cat_name].append(r)

    for user in users_permissions:
        for permission in user.PermissionIDList:
            if permission.id in permission_mapping:
                permission = permission_mapping[permission.id]
                project_id = permission.ProjectID.id
                if project_id not in project_user_mapping:
                    project_user_mapping[project_id] = []
                project_user_mapping[project_id].append(
                    {"id": user.id, "email": user.Email,
                    "read": permission.Read, "write": permission.Write,
                    "delete": permission.Delete, "admin": permission.Invite}
                )

    for user_group in user_groups:
        for permission in user_group.PermissionIDList:
            if permission.id in permission_mapping:
                permission = permission_mapping[permission.id]
                project_id = permission.ProjectID.id
                if project_id not in project_user_group_mapping:
                    project_user_group_mapping[project_id] = []
                project_user_group_mapping[project_id].append(
                    {"id": user_group.id, "name": user_group.Name,
                    "read": permission.Read, "write": permission.Write,
                    "delete": permission.Delete, "admin": permission.Invite})

    for project_id in project_id_list:
        if project_id not in project_exp_mapping:
            project_exp_mapping[project_id] = []
        if project_id not in project_sample_mapping:
            project_sample_mapping[project_id] = []
        if project_id not in project_group_mapping:
            project_group_mapping[project_id] = []
        if project_id not in project_category_mapping:
            project_category_mapping[project_id] = {}
        if project_id not in project_user_mapping:
            project_user_mapping[project_id] = []
        if project_id not in project_user_group_mapping:
            project_user_group_mapping[project_id] = []

    results = []
    for project in project_list:
        result = {
            "_id": project.get("_id"),
            "Name": project.get("Name"),
            "ShortID": project.get("ShortID"),
            "experiments": project_exp_mapping.get(project.get("_id"), []),
            "samples": project_sample_mapping.get(project.get("_id"), []),
            "groups": project_group_mapping.get(project.get("_id"), []),
            "units": unitDict.get(project.get("_id"), []),
            "fields": fieldDict.get(project.get("_id"), []),
            "researchitems": {},
            "permissions": {
                "owner": users_owner_mapping.get(project["OwnerID"], {"id": None, "email": None}),
                "users": project_user_mapping.get(project.get("_id"), []),
                "usergroups": project_user_group_mapping.get(project.get("_id"), [])
            }}

        for cat_name in project_category_mapping[project.get("_id")]:
            result["researchitems"].update({
                cat_name: project_category_mapping[project.get("_id")][cat_name]
            })
        results.append(result)
    return results



@bp.route('/<project_id>', methods=['GET'])
@response_wrapper
def get(project_id):
    """Get a project by its ID.
    ---
    get:
        parameters:
        - in: path
          schema: IdInputSchema
        responses:
            200:
                description: A project object
                content:
                    application/json:
                        schema: ProjectSchema
    """
    from mongo_engine.Project import Project

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, "read")
    if not access:
        PermissionError("You do not have permission to access this project.")
    results = get_many_projects([project_id])
    result = results[0]
    dumped = ProjectSchema().dump(result)
    return dumped

    
@bp.route('', methods=['GET'])
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_all(data:dict):
    """Get all projects.
    ---
    get:
        parameters:
        - in: path
          schema: QueryInputSchema
        responses:
            200:
                description: A project object
                content:
                    application/json:
                        schema: ProjectAllSchema
    """
    from tenjin.mongo_engine.Project import Project
    if data:
        id_list = get_id_list_from_request_and_check_permission("Project", data, "read")
        results = get_many_projects(id_list)
        result = results[0]
        dumped = ProjectAllSchema().dump(result)
        
    else:
        projects = Project.objects().only("id", "Name", "Info")
        result = []
        for project in projects:
            if Project.check_permission_to_project(project.id, flask.g.user, "read"):
                result.append({
                    "id": str(project.id),
                    "name": project.Name,
                    "info": project.Info
                })
        dumped = ProjectAllSchema().dump(result, many=True)
    
    return dumped


@bp.route('', methods=['POST']) 
@response_wrapper
def post():
    """Create or update a project.
    ---
    post:
        parameters:
        - in: json
          schema: ProjectPostSchema
        responses:
            200:
                description: A project object
                content:
                    application/json:
                        schema: IdInputSchema
    """
    from tenjin.mongo_engine.Project import Project
    data_list = get_json_from_request()
    data_list = ProjectPostSchema().load(data_list, many=True)
    return_id_list = []
    for data in data_list:
        data = None
        if "_id" not in data:
            assert "Name" in data, "Project name is required."
            param = {"Name": data["Name"]}
            project_id = Create.create("Project", param)
            data.pop("Name", None)
            data["_id"] = project_id
            
        if "_id" in data:
            project_id = bson.ObjectId(data.pop("_id"))
            access = Project.check_permission_to_project(project_id, flask.g.user, "write")
            if not access:
                raise PermissionError("You do not have permission to modify this project.")
            project = Project.objects(id=project_id).only("id").first()
            if not project:
                raise ValueError("Project not found.")
            
            # only Name and Info can be in data: Both can be updated directly
            for key in data:
                Update.update("Project", key, data[key], project_id)
        
        return_id_list.append(project_id)
        
    return project_id
           
@bp.route('/<project_id>', methods=['DELETE'])
@response_wrapper
def delete(project_id: str):
    """Delete a project.
    ---
    delete:
        parameters:
        - in: path
          schema: IdInputSchema
        responses:
            200:
                description: A project object
                content:
                    application/json:
                        schema: IdInputSchema
    """
    from tenjin.mongo_engine.Project import Project

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, "delete")
    if not access:
        raise PermissionError("You do not have permission to delete this project.")
    
    project = Project.objects(id=project_id).first()
    if not project:
        raise ValueError("Project not found.")
    
    # Perform the deletion
    Delete.delete("Project", project_id)

    return project_id
        