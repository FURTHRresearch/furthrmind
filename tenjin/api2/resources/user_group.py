import bson
import flask
from mongoengine import Q
import random
import string

from tenjin.api2.schema.user_group_schema import UserGroupSchema, UserGroupPostSchema

from tenjin.mongo_engine.User import User
from tenjin.mongo_engine.Permission import Permission
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.UserGroup import UserGroup

from .helper_methods import response_wrapper, get_json_from_request

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete

bp = flask.Blueprint("api2/usergroup", __name__)


def get_user_group_method(usergroup_id_list, mongoClient):
 

    usergroups = list(UserGroup.objects(id__in=usergroup_id_list))
    user_id_list = []
    for usergroup in usergroups:
        user_id_list.extend([u.id for u in usergroup.UserIDList])

    users = User.objects(id__in=user_id_list).only("id", "Email")
    user_mapping = {u.id: u for u in users}

    permissions_id_list = []
    for ug in usergroups:
        p_list = [p.id for p in ug.PermissionIDList]
        permissions_id_list.extend(p_list)
    permissions = list(Permission.objects(id__in=permissions_id_list))
    permission_mapping = {p.id: p for p in permissions}
    project_id_list = [p.ProjectID.id for p in permissions]

    projects = Project.objects(id__in=project_id_list)
    project_mapping = {p.id: p for p in projects}

    result_list = []
    for ug in usergroups:
        usergroup = ug.to_mongo()
        
        user_list = []
        for u in ug.UserIDList:
            user = user_mapping.get(u.id)
            if not user:
                continue
            user_list.append({"_id": str(u.id), "Email": user.Email})
        usergroup["users"] = user_list

        permission_list = []
        for permission in ug.PermissionIDList:
            permission = permission_mapping.get(permission.id)
            if not permission:
                continue
            project = project_mapping.get(permission.ProjectID.id)
            if not project:
                continue
            permission_list.append({"project": {"_id": str(project.id), "Name": project.Name},
                                    "read": permission.Read,
                                    "write": permission.Write,
                                    "delete": permission.Delete,
                                    "admin": permission.Invite})
        usergroup["permissions"] = permission_list
        result_list.append(usergroup)
    return result_list


@bp.route("/usergroup/<usergroup_id>", methods=["GET"])
@bp.route("/usergroups/<usergroup_id>", methods=["GET"])
@response_wrapper
def get_usergroup(usergroup_id: str):
    """
    Get usergroup by ID
    ---
    """

    try:
        usergroup_id = bson.ObjectId(usergroup_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid usergroup ID format.")

    usergroup = UserGroup.objects(id=usergroup_id).first()
    if not usergroup:
        raise ValueError("Usergroup not found.")

    usergroup_list = get_user_group_method([usergroup_id])

    dumped_result = UserGroupSchema().dump(usergroup_list, many=True)
    return dumped_result


@bp.route("/usergroup", methods=["GET"])
@bp.route("/usergroups", methods=["GET"])
@response_wrapper
def get_many():

    usergroup_id_list = [ug.id for ug in UserGroup.objects().only("id")]
    results = get_user_group_method(usergroup_id_list)
    dumped_results = UserGroupSchema().dump(results, many=True)
    return dumped_results


def remove_user_from_usergroup(usergroup_id: bson.ObjectId, usergroup: UserGroup):
    user_id_list = [u.id for u in usergroup.UserIDList]
    if usergroup_id in user_id_list:
        user_id_list.remove(usergroup_id)
        Update.update("UserGroup", "UserIDList", user_id_list, usergroup.id)


def add_user_to_usergroup(usergroup_id: bson.ObjectId, usergroup: UserGroup):
    user_id_list = [u.id for u in usergroup.UserIDList]
    if usergroup_id not in user_id_list:
        user_id_list.append(usergroup_id)
        Update.update("UserGroup", "UserIDList", user_id_list, usergroup.id)


        
@bp.route("/user", methods=["POST"])
@bp.route("/users", methods=["POST"])
@response_wrapper
def post():

    executing_user_id = flask.g.user
    executing_user = User.objects(id=executing_user_id).first()
    if not executing_user:
        raise ValueError("User not found.")
    
    if not executing_user.Admin:
        raise PermissionError("Only admin users can create users.")

    data_list = get_json_from_request()
    data_list = UserGroupPostSchema().load(data_list, many=True)

    return_id_list = []
    for data in data_list:

        if "_id" not in data:
            if "Name" not in data:
                raise ValueError("name is required.")

            param = {"Name": data["Name"]}

            usergroup_id = Create.create("UserGroup", param)
            data.pop("Name")
            data["_id"] = usergroup_id

        if "_id" in data:
            usergroup_id = bson.ObjectId(data.pop("_id"))


            direct_update_keys = ["Name"]
            for key in data:
                if key in direct_update_keys:
                    Update.update("User", key, data["key"], usergroup_id)
                elif key == "users":
                    # To ensure, that all users exist
                    user_id_list = [f["_id"] for f in data["users"]]
                    users = User.objects(id__in=user_id_list).only("id")
                    user_id_list = [f.id for f in users]
                    Update.update("UserGroup", "UserIDList", user_id_list, usergroup_id)
 
                elif key == "permissions":
                    usergroup = UserGroup.objects(id=usergroup_id).first()
                    permission_id_list = [p.id for p in usergroup.PermissionIDList]
                    permissions = Permission.objects(id__in=permission_id_list)
                    permission_project_mapping = {p.ProjectID.id: p for p in permissions}
                    project_id_list = []
                    for permission in data["permissions"]:
                        if "project" not in permission or "_id" not in permission["project"]:
                            raise ValueError("project with id is required in permissions.")
                        project_id = bson.ObjectId(permission["project"]["_id"])
                        project_id_list.append(project_id)
                        new_permissions = []
                        if project_id in permission_project_mapping:
                            # Update existing permission
                            p = permission_project_mapping[project_id]
                            Update.update("Permission", "Read", permission.get("read", False), p.id)
                            Update.update("Permission", "Write", permission.get("write", False), p.id)
                            Update.update("Permission", "Delete", permission.get("delete", False), p.id)
                            Update.update("Permission", "Invite", permission.get("admin", False), p.id)
                        else:
                            # Create new permission
                            param = {
                                "ProjectID": project_id,
                                "Read": permission.get("read", False),
                                "Write": permission.get("write", False),
                                "Delete": permission.get("delete", False),
                                "Invite": permission.get("admin", False),
                            }
                            permission_id = Create.create("Permission", param)
                            new_permissions.append(permission_id)                        
                    
                    # Remove permissions that are not in the new list
                    deleted_permission_id_list = []
                    for project_id in permission_project_mapping:
                        if project_id not in project_id_list:
                            permission_id = permission_project_mapping[project_id].id
                            deleted_permission_id_list.append(permission_id)
                            Delete.delete("Permission", permission_id)

                    # update user's permission list
                    if deleted_permission_id_list or new_permissions:
                        permission_id_list = [p.id for p in permission_id_list if p.id not in deleted_permission_id_list]
                        permission_id_list.extend(new_permissions)
                        Update.update("UserGroup", "PermissionIDList", permission_id_list, usergroup_id)

        return_id_list.append(usergroup_id)

    return return_id_list


@bp.route("/user/<usergroup_id>", methods=["DELETE"])
@bp.route("/users/<usergroup_id>", methods=["DELETE"])
@response_wrapper
def delete(usergroup_id: str):
    """
    Delete a user group by ID
    ---
    """
    executing_user_id = flask.g.user
    executing_user = User.objects(id=executing_user_id).first()
    if not executing_user:
        raise ValueError("User not found.")
    
    if not executing_user.Admin:
        raise PermissionError("Only admin users can delete users.")

    usergroup_id = bson.ObjectId(usergroup_id)
    usergroup = UserGroup.objects(id=usergroup_id).only("id").first()
    if not usergroup:
        raise ValueError("User group not found.")

    Delete.delete("UserGroup", usergroup_id)

    return usergroup_id
