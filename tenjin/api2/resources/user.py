import bson
import flask
from mongoengine import Q
import random
import string

from tenjin.api2.schema.user_schema import UserSchema, UserPostSchema

from tenjin.mongo_engine.User import User
from tenjin.mongo_engine.Permission import Permission
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.UserGroup import UserGroup

from .helper_methods import response_wrapper, get_json_from_request

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete

bp = flask.Blueprint("api2/user", __name__)


def get_user_method(user_id_list: list[bson.ObjectId]):

    users = list(User.objects(id__in=user_id_list))
    usergroups = UserGroup.objects(UserIDList__in=user_id_list)
    user_usergroup_mapping = {}
    for usergroup in usergroups:
        for u in usergroup.UserIDList:
            if u.id not in user_usergroup_mapping:
                user_usergroup_mapping[u.id] = []
            user_usergroup_mapping[u.id].append(
                {"id": str(usergroup.id), "name": usergroup.Name}
            )

    permissions_id_list = []
    for user in users:
        p_list = [p.id for p in user.PermissionIDList]
        permissions_id_list.extend(p_list)
    permissions = list(Permission.objects(id__in=permissions_id_list))
    permission_mapping = {p.id: p for p in permissions}
    project_id_list = [p.ProjectID.id for p in permissions]

    projects = list(
        Project.objects(Q(id__in=project_id_list) | Q(OwnerID__in=user_id_list))
    )
    project_mapping = {p.id: p for p in projects}

    owner_project_mapping = {}
    for project in projects:
        if project.OwnerID.id not in owner_project_mapping:
            owner_project_mapping[project.OwnerID.id] = []
        owner_project_mapping[project.OwnerID.id].append(project)

    result_list = []
    for u in users:
        user = u.to_mongo()

        permission_list = []
        if u.id in owner_project_mapping:
            for project in owner_project_mapping[u.id]:
                permission_list.append(
                    {
                        "project": {"_id": str(project.id), "Name": project.Name},
                        "read": True,
                        "write": True,
                        "delete": True,
                        "admin": True,
                        "owner": True,
                    }
                )

        for permission in u.PermissionIDList:
            permission = permission_mapping.get(permission.id)
            if not permission:
                continue
            project = project_mapping.get(permission.ProjectID.id)
            if not project:
                continue
            if project.OwnerID.id == u.id:
                continue
            permission_list.append(
                {
                    "project": {"_id": str(project.id), "Name": project.Name},
                    "read": permission.Read,
                    "write": permission.Write,
                    "delete": permission.Delete,
                    "admin": permission.Invite,
                    "owner": False,
                }
            )
        user["permissions"] = permission_list
        result_list.append(user)
    return result_list


@bp.route("/user/<user_id>", methods=["GET"])
@bp.route("/users/<user_id>", methods=["GET"])
@response_wrapper
def get_user(user_id: str):
    """
    Get user by ID
    ---
    """

    try:
        user_id = bson.ObjectId(user_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid user ID format.")

    user = User.objects(id=user_id).first()
    if not user:
        raise ValueError("User not found.")

    user_list = get_user_method([user_id])

    dumped_result = UserSchema().dump(user_list, many=True)
    return dumped_result


@bp.route("/user", methods=["GET"])
@bp.route("/users", methods=["GET"])
@response_wrapper
def get_many():

    user_id_list = [u.id for u in User.objects().only("id")]
    results = get_user_method(user_id_list)
    dumped_results = UserSchema().dump(results, many=True)
    return dumped_results


def generate_password():
    length = random.randint(12, 20)
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for i in range(length))
    return password


def remove_user_from_usergroup(user_id: bson.ObjectId, usergroup: UserGroup):
    user_id_list = [u.id for u in usergroup.UserIDList]
    if user_id in user_id_list:
        user_id_list.remove(user_id)
        Update.update("UserGroup", "UserIDList", user_id_list, usergroup.id)


def add_user_to_usergroup(user_id: bson.ObjectId, usergroup: UserGroup):
    user_id_list = [u.id for u in usergroup.UserIDList]
    if user_id not in user_id_list:
        user_id_list.append(user_id)
        Update.update("UserGroup", "UserIDList", user_id_list, usergroup.id)


        
@bp.route("/user", methods=["POST"])
@bp.route("/users", methods=["POST"])
@response_wrapper
def post():

    executing_user_id = flask.g.user
    executing_user = User.objects(id=executing_user_id).first()
    if not executing_user:
        raise ValueError("User not found.")

    data_list = get_json_from_request()
    data_list = UserPostSchema().load(data_list, many=True)

    return_id_list = []
    for data in data_list:

        if "_id" not in data:
            if not executing_user.is_admin():
                raise PermissionError("Only admin users can create users.")

            if "Email" not in data:
                raise ValueError("email is required.")
            if "Password" not in data:
                data["Password"] = generate_password()

            param = {"Email": data["Email"], "Password": data["Password"]}

            user_id = Create.create("User", param)
            data.pop("Password")
            data.pop("Email")
            data["_id"] = user_id

        if "_id" in data:

            user_id = bson.ObjectId(data.pop("_id"))
            if not executing_user.is_admin():
                if not executing_user.id != user_id:
                    raise PermissionError(
                        "You do not have permission to update this user."
                    )

            user = User.objects(id=user_id).first()
            if not user:
                raise ValueError("User not found.")

            direct_update_keys = ["FirstName", "LastName", "Email", "Password"]
            for key in data:
                if key in direct_update_keys:
                    Update.update("User", key, data["key"], user_id)
                elif key == "usergroups":
                    # To ensure, that all usergroups exist
                    usergroup_id_list = [f["_id"] for f in data["usergroups"]]
                    usergroups = UserGroup.objects(id__in=usergroup_id_list).only("id", "UserIDList")
                    usergroup_id_list = [f.id for f in usergroups]

                    current_usergroups = UserGroup.objects(
                        UserIDList__in=[user_id]
                    ).only("id", "UserIDList")
                    for current_ug in current_usergroups:
                        if current_ug.id not in usergroup_id_list:
                            remove_user_from_usergroup(user_id, current_ug)
                    for ug in usergroups:
                        add_user_to_usergroup(user_id, ug)
 
                elif key == "permissions":
                    user = User.objects(id=user_id).first()
                    permission_id_list = [p.id for p in user.PermissionIDList]
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
                        Update.update("User", "PermissionIDList", permission_id_list, user_id)
        
        return_id_list.append(user_id)

    return return_id_list


@bp.route("/user/<user_id>", methods=["DELETE"])
@bp.route("/users/<user_id>", methods=["DELETE"])
@response_wrapper
def delete(user_id: str):
    """
    Delete a user by ID
    ---
    """
    executing_user_id = flask.g.user
    executing_user = User.objects(id=executing_user_id).first()
    if not executing_user:
        raise ValueError("User not found.")
    
    if not executing_user.Admin:
        raise PermissionError("Only admin users can delete users.")

    user_id = bson.ObjectId(user_id)
    user = User.objects(id=user_id).only("id").first()
    if not user:
        raise ValueError("User not found.")

    Delete.delete("User", user_id)

    return user_id
