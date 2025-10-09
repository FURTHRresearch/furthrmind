import flask
import bson
from webargs.flaskparser import use_args

from tenjin.mongo_engine.Field import Field
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.ComboBoxEntry import ComboBoxEntry

from tenjin.api2.schema.field_schema import FieldSchema, FieldPostSchema
from tenjin.api2.schema.query_input_schema import QueryInputSchema

from .helper_methods import (
    get_id_list_from_request_and_check_permission,
    response_wrapper,
    get_json_from_request,
)

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete


bp = flask.Blueprint("api2/field", __name__)


def check_field_type(field_type: str):
    field_type_mapping = {
        "Numeric": ["numeric", "numeric-field", "numeric_field", "numericfield"],
        "NumericRange": [
            "numericrange",
            "numeric_range",
            "numericrangefield",
            "numeric-range-field",
            "numeric_range_field",
        ],
        "Date": ["date", "date_field", "date-field", "datefield"],
        "SingleLine": [
            "singleline",
            "single-line",
            "single_line",
            "singlelinefield",
            "single-line-field",
            "single_line_field",
            "text",
            "text-field",
            "text_field",
            "textfield",
        ],
        "ComboBox": [
            "combobox",
            "comboboxfield",
            "combobox-field",
            "combobox_field",
            "comboboxentry",
            "list",
            "listfield",
            "list-field",
            "list_field",
        ],
        "MultiLine": [
            "multiline",
            "multi_line",
            "mulit-line",
            "multilinefield",
            "multi-line-field",
            "multi_line_field",
            "notebook-field",
            "notebook_field",
            "notebookfield",
        ],
        "CheckBox": ["checkbox", "checkbox-field", "checkbox_field", "checkboxfield"],
        "Calculation": [
            "calculation",
            "calculation-field",
            "calculation_field",
            "calculationfield",
        ],
    }
    field_type = field_type.lower()
    for key, values in field_type_mapping.items():
        if field_type in values:
            return key
    raise ValueError(f"Invalid field type: {field_type}.")


def check_field_by_name_and_create_if_not_exists(
    field_name: str, field_type, project_id: str
):
    field = Field.objects(NameLower=field_name.lower(), ProjectID=project_id).first()
    if not field:
        if field_type is None:
            raise ValueError("Field type is required.")
        field_type = check_field_type(field_type)
        parameter = {"Name": field_name, "ProjectID": project_id, "Type": field_type}
        field_id = Create.create("Field", parameter)
    else:
        field_id = field.id
    return field_id


@bp.route("/<project_id>/field/<field_id>", methods=["GET"])
@bp.route("/<project_id>/fields/<field_id>", methods=["GET"])
@response_wrapper
def get_field(project_id: str, field_id: str):
    """
    Get field by ID
    ---
    """
    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    try:
        field_id = bson.ObjectId(field_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid field data ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read field data in this project."
        )

    field = Field.objects(id=field_id, ProjectID=project_id).first()
    if not field:
        raise ValueError("Field not found.")
    if field.Type == "ComboBox":
        comboboxentries = ComboBoxEntry.objects(FieldID=field.id).only("id", "Name")
    else:
        comboboxentries = []
    field = field.to_mongo()
    field["comboboxentries"] = [c.to_mongo() for c in comboboxentries]

    dumped_result = FieldSchema().dump([field], many=True)
    return dumped_result


@bp.route("/<project_id>/field", methods=["GET"])
@bp.route("/<project_id>/fields", methods=["GET"])
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_many(args, project_id: str):

    project_id = bson.ObjectId(project_id)

    if args:
        id_list = get_id_list_from_request_and_check_permission(
            "Field", args, "read", project_id=project_id
        )
        fields = list(Field.objects(id__in=id_list, ProjectID=project_id))
    else:
        access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
        if not access:
            raise PermissionError(
                "You do not have permission to read columns in this project."
            )
        fields = list(Field.objects(ProjectID=project_id))
    id_list = [f.id for f in fields]
    comboboxentries = ComboBoxEntry.objects(FieldID__in=id_list).only(
        "id", "Name", "FieldID"
    )
    comboboxentries = [c.to_mongo() for c in comboboxentries]
    combo_dict = {}
    for c in comboboxentries:
        if c["FieldID"] not in combo_dict:
            combo_dict[c["FieldID"]] = []
        combo_dict[c["FieldID"]].append(c)
    results = []
    for f in fields:
        f = f.to_mongo()
        if f["_id"] in combo_dict:
            f["comboboxentries"] = combo_dict[f["_id"]]
        else:
            f["comboboxentries"] = []
        results.append(f)
    dumped_results = FieldSchema().dump(results, many=True)
    return dumped_results


@bp.route("/<project_id>/field", methods=["POST"])
@bp.route("/<project_id>/fields", methods=["POST"])
@response_wrapper
def post(project_id: str):
    data_list = get_json_from_request()
    data_list = FieldPostSchema().load(data_list, many=True)

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="write")
    if not access:
        PermissionError(
            "You do not have permission to create or update a group in this project."
        )
    field_id_list =[]
    for data in data_list:
        if "_id" not in data:
            assert "Name" in data, "Field name is required."
            assert "Type" in data, "Field type is required."
            data["ProjectID"] = project_id
            param = {
                "ProjectID": project_id,
                "Name": data["Name"],
                "Type": data["Type"],
            }
            field_id = Create.create("Field", param)
            data.pop("Name")
            data["_id"] = field_id
            

        if "_id" in data:
            field_id = bson.ObjectId(data.pop("_id"))
            field = Field.objects(id=field_id, ProjectID=project_id).first()
            if not field:
                raise ValueError("Field not found.")
            field_id_list.append(str(field_id))
            direct_update_keys = ["Name"]
            for key in data:
                if key in direct_update_keys:
                    Update.update("Field", key, data[key], field_id)

    return  field_id_list


@bp.route("/<project_id>/field/<field_id>", methods=["DELETE"])
@bp.route("/<project_id>/fields/<field_id>", methods=["DELETE"])
@response_wrapper
def delete(project_id: str, field_id: str):
    """
    Delete a field by ID
    ---
    """
    from mongo_engine.Project import Project
    from mongo_engine.Group import Group

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(
        project_id, flask.g.user, flag="delete"
    )
    if not access:
        PermissionError("You do not have permission to delete this field.")

    field_id = bson.ObjectId(field_id)
    field = Field.objects(id=field_id, ProjectID=project_id).first()
    if not field:
        raise ValueError("Field not found.")

    Delete.delete("Field", field_id)

    return field_id
