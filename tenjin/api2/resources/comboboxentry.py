import flask
import bson
from webargs.flaskparser import use_args

from tenjin.mongo_engine.Field import Field
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.ComboBoxEntry import ComboBoxEntry
from tenjin.mongo_engine.File import File

from tenjin.api2.schema.comboboxentry_schema import (
    ComboBoxEntrySchema,
    ComboBoxEntryPostSchema,
)
from tenjin.api2.schema.query_input_schema import QueryInputSchema

from .helper_methods import (
    get_id_list_from_request_and_check_permission,
    response_wrapper,
    get_json_from_request,
)

from .fielddata import get_fielddata_method, update_or_create_fielddata_method
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete


bp = flask.Blueprint("api2/comboboxentry", __name__)


def get_combo_method(project_id: bson.ObjectId, combo_id_list: list[bson.ObjectId]):
    combos = list(
        ComboBoxEntry.objects(id__in=combo_id_list, ProjectID=project_id).only(
            "id", "Name", "FieldID", "FileIDList", "FieldDataIDList"
        )
    )
    comboboxentries = [c.to_mongo() for c in combos]
    field_id_list = [c["FieldID"] for c in comboboxentries]
    file_id_list = []
    field_data_id_list = []
    for c in comboboxentries:
        field_data_id_list.extend(c["FieldDataIDList"])
        file_id_list.extend(c["FileIDList"])

    fields = Field.objects(id__in=field_id_list).only("id", "Name")
    field_mapping = {f.id: f.to_mongo() for f in fields}

    fielddata = get_fielddata_method(project_id, field_data_id_list)
    fielddata_mapping = {fd["_id"]: fd for fd in fielddata}

    files = File.objects(id__in=file_id_list).only("id", "Name")
    file_mapping = {f.id: f.to_mongo() for f in files}
    results = []

    for c in comboboxentries:
        c["field"] = (
            field_mapping[c["FieldID"]] if c["FieldID"] in field_mapping else None
        )
        c["files"] = [
            file_mapping[fid] for fid in c["FileIDList"] if fid in file_mapping
        ]
        c["fielddata"] = [
            fielddata_mapping[fd_id]
            for fd_id in c["FieldDataIDList"]
            if fd_id in fielddata_mapping
        ]
        results.append(c)
    return results


@bp.route("/<project_id>/comboboxentry/<combo_id>", methods=["GET"])
@bp.route("/<project_id>/comboboxentries/<combo_id>", methods=["GET"])
@response_wrapper
def get_combo(project_id: str, combo_id: str):
    """
    Get combobox entry by ID
    ---
    """
    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    try:
        combo_id = bson.ObjectId(combo_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid combobox entry ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read field data in this project."
        )

    combo = ComboBoxEntry.objects(id=combo_id, ProjectID=project_id).first()
    if not combo:
        raise ValueError("ComboBox entry not found.")

    combo_list = get_combo_method(project_id, [combo_id])

    dumped_result = ComboBoxEntrySchema().dump(combo_list, many=True)
    return dumped_result


@bp.route("/<project_id>/comboboxentry", methods=["GET"])
@bp.route("/<project_id>/comboboxentries", methods=["GET"])
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_many(args, project_id: str):

    project_id = bson.ObjectId(project_id)

    if args:
        id_list = get_id_list_from_request_and_check_permission(
            "ComboBoxEntry", args, "read", project_id=project_id, only_id_allowed=True
        )

    else:
        access = Project.check_permission_to_project(
            project_id, flask.g.user, flag="write"
        )
        if not access:
            raise PermissionError(
                "You do not have permission to read combobox entries in this project."
            )
        comboentries = ComboBoxEntry.objects(ProjectID=project_id).only("id")
        id_list = [c.id for c in comboentries]

    results = get_combo_method(project_id, id_list)
    dumped_results = ComboBoxEntrySchema().dump(results, many=True)
    return dumped_results


@bp.route("/<project_id>/comboboxentry", methods=["POST"])
@bp.route("/<project_id>/comboboxentries", methods=["POST"])
@response_wrapper
def post(project_id: str):

    data_list = get_json_from_request()
    data_list = ComboBoxEntryPostSchema().load(data_list, many=True)

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="write")
    if not access:
        PermissionError(
            "You do not have permission to create or update a group in this project."
        )

    return_id_list = []
    for data in data_list:

        if "_id" not in data:
            if "Name" not in data:
                raise ValueError("name is required.")
            if "field" not in data or "_id" not in data["field"]:
                raise ValueError("field with id is required.")
            field_id = bson.ObjectId(data["field"]["_id"])
            field = Field.objects(id=field_id, ProjectID=project_id).first()
            if not field:
                raise ValueError("Field not found.")

            param = {"ProjectID": project_id, "Name": data["Name"], "FieldID": field_id}

            combo_id = Create.create("ComboBoxEntry", param)
            data.pop("field")
            data.pop("Name")
            data["_id"] = combo_id

        if "_id" in data:
            combo_id = bson.ObjectId(data.pop("_id"))
            combo = ComboBoxEntry.objects(id=combo_id, ProjectID=project_id).first()
            if not combo:
                raise ValueError("ComboBoxEntry not found.")

            direct_update_keys = ["Name"]
            for key in data:
                if key in direct_update_keys:
                    Update.update("ComboBoxEntry", key, data["key"], combo_id)
                elif key == "files":
                    # To ensure, that all files exist
                    file_id_list = [f["_id"] for f in data["files"]]
                    files = File.objects(id__in=file_id_list).only("id")
                    existing_file_id_list = [f.id for f in files]
                    file_id_list = [
                        f_id for f_id in file_id_list if f_id in existing_file_id_list
                    ]
                    Update.update("ComboBoxEntry", "FileIDList", file_id_list, combo_id)
                elif key == "fielddata":
                    fielddata_arg_list = data["fielddata"]
                    fielddata_id_list = []
                    for fielddata_arg in fielddata_arg_list:
                        fielddata_id = update_or_create_fielddata_method(
                            fielddata_arg, project_id
                        )
                        fielddata_id_list.append(fielddata_id)
                    Update.update(
                        "ComboBoxEntry", "FieldDataIDList", fielddata_id_list, combo_id
                    )

        return_id_list.append(combo_id)

    return return_id_list


@bp.route("/<project_id>/comboboxentry/<combo_id>", methods=["DELETE"])
@bp.route("/<project_id>/comboboxentries/<combo_id>", methods=["DELETE"])
@response_wrapper
def delete(project_id: str, combo_id: str):
    """
    Delete a comboboxentry by ID
    ---
    """

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(
        project_id, flask.g.user, flag="delete"
    )
    if not access:
        PermissionError("You do not have permission to delete this field.")

    combo_id = bson.ObjectId(combo_id)
    combo = ComboBoxEntry.objects(id=combo_id, ProjectID=project_id).first()
    if not combo:
        raise ValueError("ComboBoxEntry not found.")

    Delete.delete("ComboBoxEntry", combo_id)

    return combo_id
