import json
from datetime import datetime

import bson
import bson.json_util
import flask
import asyncio

from tenjin.cache import Cache
from tenjin.database.db import get_db
from tenjin.execution.append import Append
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete
from tenjin.execution.update import Update
from tenjin.logic.copy_template import (
    copy,
    createNewFields,
    createNewUnits,
    updateUnitDefinitions,
    createNewComboEntries,
    copyFieldDataOfComboEntries,
    createNewUnitCategoriesAndUpdateNewUnits,
)
from tenjin.tasks.rq_task import create_task
# from tenjin.web.helper.filterHelper import get_project_index
from tenjin.web.helper.group_mapping import get_page_group_mapping
from tenjin.web.helper.group_index import get_group_index
from .auth import login_required
from .helper.furthrHelper import ensureAccess

cache = Cache.get_cache()

bp = flask.Blueprint("webprojects", __name__)


@bp.route("/projects")
@login_required
def projects():
    from tenjin.mongo_engine.Project import Project
    from tenjin.mongo_engine.User import User

    projects = Project.objects()
    access_list = []
    for project in projects:
        if Project.check_permission_to_project(
            project.id, bson.ObjectId(flask.g.user), "read"
        ):
            access_list.append(project)

    user = User.objects().only("id", "Email")
    user_mapping = {u.id: u.Email for u in user}
    projects = []
    for p in access_list:
        owner = "No owner"
        if p.OwnerID:
            owner = user_mapping.get(p.OwnerID.id, "No owner")
        projects.append(
            {
                "id": str(p["id"]),
                "Name": p["Name"],
                "info": p["Info"],
                "date": p["Date"].isoformat() if p["Date"] else None,
                "owner": owner,
                "archived": p["Archived"],
            }
        )

    return bson.json_util.dumps(reversed(projects))


@bp.route("/projects/<project_id>/groups")
@login_required
def project_groups(project_id):
    from tenjin.mongo_engine.Group import Group

    name = flask.request.args.get("name", None)

    if name:
        groups = (
            Group.objects(ProjectID=project_id, NameLower__contains=name.lower())
            .order_by("-Date")
            .only("Name", "id")
        )
    else:
        groups = Group.objects(ProjectID=project_id).order_by("Name").only("Name", "id")

    result = []

    category = "Last 50 groups"
    if name:
        category = f"Groups contain '{name}'"
    for g in groups[:50]:
        result.append(
            {
                "id": str(g.id),
                "Name": g["Name"],
                "Category": "Group",
                "DisplayedCategory": category,
            }
        )

    return result


@bp.route("/projects/<id>/collaborators")
@login_required
def project_collaborators(id):
    db = get_db().db
    permissions = list(db.Permission.find({"ProjectID": bson.ObjectId(id)}))
    usergroups = [
        {
            "type": "group",
            "id": str(g["_id"]),
            "name": g["Name"],
            "PermissionIDList": g["PermissionIDList"],
        }
        for g in db.UserGroup.find(
            {
                "PermissionIDList": {
                    "$elemMatch": {"$in": [p["_id"] for p in permissions]}
                }
            }
        )
    ]
    users = [
        {
            "type": "user",
            "id": str(c["_id"]),
            "email": c["Email"],
            "PermissionIDList": c["PermissionIDList"],
        }
        for c in db.User.find(
            {
                "PermissionIDList": {
                    "$elemMatch": {"$in": [p["_id"] for p in permissions]}
                }
            }
        )
    ]
    collaborators = [*usergroups, *users]
    for c in collaborators:
        permission = next(
            (p for p in permissions if p["_id"] in c["PermissionIDList"]), None
        )
        c.pop("PermissionIDList")
        c["read"] = permission["Read"]
        c["write"] = permission["Write"]
        c["delete"] = permission["Delete"]
        c["invite"] = permission["Invite"]
        c["permissionId"] = str(permission["_id"])
    return json.dumps(collaborators)


@bp.route("/projects/<id>/collaborators", methods=["POST"])
@login_required
def add_project_collaborator(id):
    data = flask.request.get_json()
    userId = flask.g.user
    permissionId = Create.create(
        "Permission",
        {
            "ProjectID": bson.ObjectId(id),
            "Write": False,
            "Read": True,
            "Delete": False,
            "Invite": False,
        },
        get_db(),
        userId,
    )

    if data.get("userId", False):
        Append.append(
            "User",
            "PermissionIDList",
            bson.ObjectId(data["userId"]),
            permissionId,
            get_db(),
            userId,
        )
    if data.get("groupId", False):
        Append.append(
            "UserGroup",
            "PermissionIDList",
            bson.ObjectId(data["groupId"]),
            permissionId,
            get_db(),
            userId,
        )

    return "all good"


@bp.route("/projects/<id>/settings")
@login_required
def project_settings(id):
    from tenjin.mongo_engine.User import User
    from tenjin.mongo_engine.Project import Project

    ensureAccess("Project", "read", id)
    db = get_db().db
    project = db.Project.find_one({"_id": bson.ObjectId(id)})
    user_id = flask.g.user
    user = User.objects(id=user_id).first()

    result_list, result_dict = Project.check_delete_or_archive_permission(
        [bson.ObjectId(id)], user
    )
    if result_list:
        delete = True
    else:
        delete = False

    return {
        "id": str(project["_id"]),
        "name": project["Name"],
        "info": project["Info"],
        "owner": str(project["OwnerID"]),
        "ownerEmail": (
            db.User.find_one({"_id": project["OwnerID"]}).get("Email", "")
            if project.get("OwnerID", False)
            else ""
        ),
        "delete": delete,
        "archived": project["Archived"],
    }


@bp.route("/projects/<id>/groupindex")
@login_required
async def groupindex(id):
    comboFilter = json.loads(flask.request.args.get("comboFieldValues", "[]"))
    numericFilter = json.loads(flask.request.args.get("numericFilter", "[]"))
    dateFilter = json.loads(flask.request.args.get("dateFilter", "[]"))
    dateFilterNeu = []
    dateCreated = None
    for df in dateFilter:
        if df["field"] == "date_created":
            dateCreated = df
        else:
            dateFilterNeu.append(df)
    dateFilter = dateFilterNeu
    textFilter = json.loads(flask.request.args.get("textFilter", "[]"))
    checkFilter = json.loads(flask.request.args.get("checkFilter", "[]"))

    groupFilter = json.loads(flask.request.args.get("groupFilter", "[]"))
    group_id_list = json.loads(flask.request.args.get("groupIDs", "[]"))
    group_id_list = [bson.ObjectId(g) for g in group_id_list]
    
    sampleFilter = json.loads(flask.request.args.get("sampleFilter", "[]"))
    experimentFilter = json.loads(flask.request.args.get("experimentFilter", "[]"))
    research_item_filter = json.loads(
        flask.request.args.get("researchItemFilter", "[]")
    )
    recent = flask.request.args.get("recent", "false")
    index = flask.request.args.get("index", "0")
    include_linked = flask.request.args.get("includeLinked", "")
    displayed_categories = json.loads(
        flask.request.args.get("displayedCategories", "[]")
    )
    if recent == "true":
        recent = True
    else:
        recent = False

    if include_linked == "false":
        include_linked = "none"

    index = int(index)
    project_id = bson.ObjectId(id)

    from tenjin.mongo_engine.Project import Project

    document_list_original, result_dict = Project.check_permission(
        [project_id], "read", flask.g.user
    )
    if not document_list_original:
        return []


    grouplist = await get_group_index(
        project_id,
        group_id_list,
        flask.request.args.get("nameFilter"),
        comboFilter,
        numericFilter,
        groupFilter,
        sampleFilter,
        experimentFilter,
        research_item_filter,
        recent=recent,
        include_linked=include_linked,
        date_filter=dateFilter,
        date_created=dateCreated,
        text_filter=textFilter,
        checks_filter=checkFilter,
        displayed_categories=displayed_categories,
    )
    return json.dumps(grouplist)


@bp.route("/projects/<project_id>/page-group-mapping")
@login_required
async def page_group_mapping(project_id):
    name_filter = flask.request.args.get("nameFilter", "")
    comboFilter = json.loads(flask.request.args.get("comboFieldValues", "[]"))
    numericFilter = json.loads(flask.request.args.get("numericFilter", "[]"))
    dateFilter = json.loads(flask.request.args.get("dateFilter", "[]"))
    dateFilterNeu = []
    dateCreated = None
    for df in dateFilter:
        if df["field"] == "date_created":
            dateCreated = df
        else:
            dateFilterNeu.append(df)
    dateFilter = dateFilterNeu
    textFilter = json.loads(flask.request.args.get("textFilter", "[]"))
    checkFilter = json.loads(flask.request.args.get("checkFilter", "[]"))

    groupFilter = json.loads(flask.request.args.get("groupFilter", "[]"))
    sampleFilter = json.loads(flask.request.args.get("sampleFilter", "[]"))
    experimentFilter = json.loads(flask.request.args.get("experimentFilter", "[]"))
    research_item_filter = json.loads(
        flask.request.args.get("researchItemFilter", "[]")
    )
    recent = flask.request.args.get("recent", "false")
    displayed_categories = json.loads(
        flask.request.args.get("displayedCategories", "[]")
    )
    include_linked = flask.request.args.get("includeLinked", "")

    if recent == "true":
        recent = True
    else:
        recent = False

    if include_linked == "false":
        include_linked = "none"

    project_id = bson.ObjectId(project_id)
    from tenjin.mongo_engine.Project import Project

    document_list_original, result_dict = Project.check_permission(
        [project_id], "read", flask.g.user
    )
    if not document_list_original:
        return {}

    page_group_mapping = await get_page_group_mapping(
        project_id,
        name_filter,
        comboFilter,
        numericFilter,
        groupFilter,
        sampleFilter,
        experimentFilter,
        research_item_filter,
        recent=recent,
        date_filter=dateFilter,
        date_created=dateCreated,
        text_filter=textFilter,
        check_filter=checkFilter,
        displayed_categories=displayed_categories,
        include_linked=include_linked,
    )
    # coroutine = get_page_group_mapping(
    #     project_id,
    #     name_filter,
    #     comboFilter,
    #     numericFilter,
    #     groupFilter,
    #     sampleFilter,
    #     experimentFilter,
    #     research_item_filter,
    #     recent=recent,
    #     date_filter=dateFilter,
    #     date_created=dateCreated,
    #     text_filter=textFilter,
    #     checkFilter=checkFilter,
    #     displayed_categories=displayed_categories,
    #     include_linked=include_linked,)
    # page_group_mapping = asyncio.gather(coroutine)
    return json.dumps(page_group_mapping)


@bp.route("/projects/<id>/categories")
@login_required
def project_categories(id):
    return json.dumps(
        [
            {
                "id": str(c["_id"]),
                "name": c["Name"],
                "description": c["Description"] if "Description" in c else "",
            }
            for c in get_db().db.ResearchCategory.find({"ProjectID": bson.ObjectId(id)})
        ]
    )


@bp.route("/projects", methods=["POST"])
@login_required
def create_project():
    data = flask.request.get_json()
    userId = flask.g.user
    info = data["description"] if data["description"] else "No Description"

    parameter = {
        "Name": data["name"],
        "Info": info,
    }
    projId = Create.create("Project", parameter, get_db(), userId)

    Create.create(
        "Group",
        {
            "Name": "Default group",
            "ProjectID": projId,
        },
        get_db(),
        userId,
    )
    return json.dumps(
        {
            "id": str(projId),
            "Name": data["name"],
            "info": data["description"],
            "date": datetime.now().isoformat(),
            "owner": get_db().db.User.find_one({"_id": flask.g.user})["Email"],
        }
    )


@bp.route("/projects/check", methods=["POST"])
@login_required
def check_name():
    from tenjin.mongo_engine.Project import Project

    data = flask.request.get_json()
    name = data.get("name")
    param = {
        "Name": name,
    }

    doc = Project(**param)

    try:
        doc.validate(clean=True)
        return "True"
    except:
        return "False"


@bp.route("/projects/<project_id>/archive", methods=["POST"])
@login_required
def archive_project(project_id):
    from tenjin.mongo_engine.Project import Project

    project = Project.objects(id=bson.ObjectId(project_id)).first()
    update_value = not project.Archived
    Update.update("Project", "Archived", update_value, bson.ObjectId(project_id))
    return "done"


@bp.route("/projects/<project_id>", methods=["DELETE"])
@login_required
def delete_project(project_id):
    Delete.delete("Project", bson.ObjectId(project_id))
    return "done"


@bp.route("/projects/<id>", methods=["POST"])
@login_required
def update_project(id):
    ensureAccess("Project", "write", id)
    projId = bson.ObjectId(id)
    userId = flask.g.user
    data = flask.request.get_json()
    if "name" in data:
        Update.update("Project", "Name", data["name"], projId, get_db(), userId)
    if "info" in data:
        Update.update("Project", "Info", data["info"], projId, get_db(), userId)
    return "done"


@bp.route("/permissions/<id>", methods=["POST"])
@login_required
def update_permission(id):
    ensureAccess("Permission", "write", id)
    permissionId = bson.ObjectId(id)
    userId = flask.g.user
    data = flask.request.get_json()

    send_email = False
    if "read" in data:
        if not "write" in data and not "delete" in data and not "invite" in data:
            send_email = True
        Update.update(
            "Permission",
            "Read",
            data["read"],
            permissionId,
            get_db(),
            userId,
            send_email=send_email,
        )

    if "write" in data:
        if not "delete" in data and not "invite" in data:
            send_email = True
        Update.update(
            "Permission",
            "Write",
            data["write"],
            permissionId,
            get_db(),
            userId,
            send_email=send_email,
        )

    if "delete" in data:
        if not "invite" in data:
            send_email = True
        Update.update(
            "Permission",
            "Delete",
            data["delete"],
            permissionId,
            get_db(),
            userId,
            send_email=send_email,
        )

    if "invite" in data:
        Update.update(
            "Permission",
            "Invite",
            data["invite"],
            permissionId,
            get_db(),
            userId,
            send_email=True,
        )
    return "done"


@bp.route("/permissions/<permission_id>", methods=["DELETE"])
@login_required
def remove_permission(permission_id):
    permission_id = bson.ObjectId(permission_id)
    Delete.delete("Permission", permission_id)
    return "done"


@bp.route("/permissions/<project_id>", methods=["GET"])
@login_required
def has_permission(project_id):
    from tenjin.mongo_engine.Project import Project

    userId = flask.g.user

    flag = Project.check_permission_to_project(
        bson.ObjectId(project_id), bson.ObjectId(userId), "invite"
    )
    if flag:
        return "admin"

    flag = Project.check_permission_to_project(
        bson.ObjectId(project_id), bson.ObjectId(userId), "write"
    )
    if flag:
        return "write"
    else:
        return "read"


@bp.route("/projects/<project_id>/owner", methods=["POST"])
@login_required
def change_owner(project_id):
    from tenjin.mongo_engine import Database

    data = flask.request.get_json()
    user_id = data.get("userId")
    # Avoid access check
    try:
        Database.set_no_access_check(True)
        Update.update(
            "Project", "OwnerID", bson.ObjectId(user_id), bson.ObjectId(project_id)
        )
    except Exception as e:
        raise e
    finally:
        Database.set_no_access_check(False)

    return "done"


@bp.route("/projects/<project_id>/clone", methods=["POST"])
@login_required
def clone_project(project_id):
    from tenjin.mongo_engine.Project import Project
    from tenjin.mongo_engine.Group import Group
    from tenjin.mongo_engine.ResearchCategory import ResearchCategory
    from tenjin.database.db import get_db

    data = flask.request.get_json()

    original_project = Project.objects(id=bson.ObjectId(project_id)).first()
    description = original_project.Info

    check = False
    name = f"Copy of {original_project.Name}"
    parameter = {
        "Name": name,
        "Info": description,
    }
    number = 1
    while not check:
        try:
            doc = Project(**parameter)
            doc.validate(clean=True)
            break
        except:
            parameter["Name"] = f"{name} {number}"
            number += 1

    new_project_id = Create.create("Project", parameter)

    include_data = data.get("includeData")
    include_files = data.get("includeFile")

    # Research Categories
    cats = ResearchCategory.objects(ProjectID=bson.ObjectId(project_id))
    for cat in cats:
        cat_dict = {"Name": cat.Name, "ProjectID": new_project_id}
        Create.create("ResearchCategory", cat_dict)

    # ----------------------------------------------------------------------------------
    # fields
    fields = list(get_db().db.Field.find({"ProjectID": bson.ObjectId(project_id)}))
    new_fields = createNewFields(fields, new_project_id, flask.g.user)

    # create a mapping between original fieldID and the new fields. This is needed to create the fieldData later on
    original_field_id_new_field_mapping = {}
    for field in fields:
        for new_field in new_fields:
            if field["Name"] == new_field["Name"]:
                original_field_id_new_field_mapping[field["_id"]] = new_field
                break

    # ------------------------------------------------------------------------------------
    # units

    units = list(get_db().db.Unit.find({"ProjectID": bson.ObjectId(project_id)}))
    new_units = createNewUnits(units, new_project_id, flask.g.user)
    # create a mapping between original unitID and the new unit. This is needed for updating the unit definitions
    original_unit_id_new_unit_mapping = {}
    new_unit_id_original_unit_mapping = {}
    for unit in units:
        for new_unit in new_units:
            if unit["ShortName"] == new_unit["ShortName"]:
                original_unit_id_new_unit_mapping[unit["_id"]] = new_unit
                new_unit_id_original_unit_mapping[new_unit["_id"]] = unit
                break
    
    # update orginal unit mapping with predefined, otherwise the predefined units 
    # will not be available when using them for creating field_data of comboEntries
    predefined_units = list(get_db().db.Unit.find({"Predefined": True}))
    for predefined_unit in predefined_units:
        original_unit_id_new_unit_mapping[predefined_unit["_id"]] = predefined_unit
    
    updateUnitDefinitions(
        new_units,
        new_unit_id_original_unit_mapping,
        original_unit_id_new_unit_mapping,
        flask.g.user,
    )
    createNewUnitCategoriesAndUpdateNewUnits(
        units, original_unit_id_new_unit_mapping, new_project_id, flask.g.user
    )

    # ------------------------------------------------------------------------------
    # combobox entries
    original_combo_field_list = [
        field for field in fields if field["Type"] == "ComboBox"
    ]
    new_combo_field_list = [
        field for field in new_fields if field["Type"] == "ComboBox"
    ]

    # create all comboBoxEntries and get all original fieldData per new comboBoxEntryID =>
    # mapping with newComboEntryID as key and original field_data_id_list as value
    # the newComboEntryID is needed, to attach the new fieldData (not created yet) to the right comboEntry
    combo_entry_field_data_mapping, original_combo_id_new_combo_id_mapping = (
        createNewComboEntries(
            original_combo_field_list, new_combo_field_list, flask.g.user, new_project_id
        )
    )
    field_data_id_list = []
    for _field_data_id_list in combo_entry_field_data_mapping.values():
        field_data_id_list.extend(_field_data_id_list)

    original_field_data_list = list(
        get_db().db.FieldData.find({"_id": {"$in": field_data_id_list}})
    )
    original_field_data_mapping = {
        fieldData["_id"]: fieldData for fieldData in original_field_data_list
    }

    copyFieldDataOfComboEntries(
        combo_entry_field_data_mapping,
        original_field_data_mapping,
        original_field_id_new_field_mapping,
        original_combo_id_new_combo_id_mapping,
        original_unit_id_new_unit_mapping,
        bson.ObjectId(new_project_id),
        flask.g.user,
    )

    # -----------------------------------------------------------------------------------------
    # copy data

    if include_data:
        # only parents
        old_groups = Group.objects(ProjectID=bson.ObjectId(project_id), GroupID=None)

        for g in old_groups:
            create_task(
                copy,
                template_id=g.id,
                collection="Group",
                project_id=bson.ObjectId(new_project_id),
                user_id=flask.g.user,
                include_fields=True,
                include_raw_data=True,
                include_files=include_files,
                include_exp=True,
                include_sample=True,
                include_researchitem=True,
                include_subgroup=True,
                do_linking=True,
            )
    else:
        Create.create(
            "Group",
            {
                "Name": "Default group",
                "ProjectID": new_project_id,
            },
        )
    return "done"
