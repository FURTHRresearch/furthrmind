import bson
import flask
from typing import List
from mongoengine import Q
from webargs.flaskparser import use_args

from tenjin.api2.resources.helper_methods import response_wrapper, get_json_from_request
from tenjin.api2.resources.helper_methods import get_id_list_from_request_and_check_permission

from tenjin.api2.schema.column_schema import ColumnSchema, ColumnPostSchema
from tenjin.api2.schema.get_all_standard_schema import GetAllStandardSchema
from tenjin.api2.schema.query_input_schema import QueryInputSchema

from tenjin.execution.update import Update
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete


from tenjin.mongo_engine.Project import Project

from tenjin.mongo_engine.RawData import RawData
from tenjin.mongo_engine.Column import Column
from mongo_engine.Project import Project
from mongo_engine.Unit import Unit


bp = flask.Blueprint("api2/column", __name__)

def update_or_create_column_method(
    args: dict, project_id: bson.ObjectId
) -> bson.ObjectId:
    """
    Process field data from any other collection.
    """
    if "_id" not in args:
        if "Name" not in args:
            raise ValueError("Name is required to create a new column.")
        if not "Type" in args:
            raise ValueError("Type is required to create a new column.")

        column_id = create_column(args["Name"], args["Type"], project_id)
        args["_id"] = column_id

    if "_id" in args:
        column_id = bson.ObjectId(args["_id"])
        if "values" in args:
            "Type checks are done by mongoengine before writing data to mongodb"
            Update.update("Column", "Data", args["values"], column_id)
        if "unit" in args and args["unit"] is not None:
            update_column_unit(column_id, args["unit"], project_id)

    return column_id


def create_column(name, column_type, project_id):

    parameter = {
        "Name": name,
        "Type": column_type,
        "ProjectID": project_id
    }

    column_id = Create.create("Column", parameter)
    return column_id


def update_column_unit(
    column_id, unit_dict: None | dict, project_id: bson.ObjectId = None
):  
    column = Column.objects(id=column_id, ProjectID=project_id).first()
    if not column:
        raise ValueError("Column not found.")

    if column.Type not in ["Numeric"]:
        raise ValueError("Column type must be Numeric for unit updates.")

    if unit_dict is None:
        Update.update("Column", "UnitID", None, column_id)
        return

    unit = None
    if "id" in unit_dict:
        try:
            unit_id = bson.ObjectId(unit_dict["id"])
        except bson.errors.InvalidId:
            raise ValueError("Invalid ObjectId format.")
        query = Q(id=unit_id) & Q(ProjectID=project_id) | Q(id=unit_id) & Q(
            Predefined=True
        )
        unit = Unit.objects(id=unit_id).first()
        if not unit:
            raise ValueError(
                f"Unit with id '{unit_dict['id']}' not found in this project."
            )

    elif "ShortName" in unit_dict:
        query = Q(ShortName=unit_dict["ShortName"]) & Q(
            ProjectID=project_id
        ) | Q(ShortName=unit_dict["ShortName"]) & Q(Predefined=True)
        unit = Unit.objects(query).first()
        if not unit:
            raise ValueError(
                f"Unit with ShortName '{unit_dict['ShortName']}' not found in this project."
            )
    if unit is None:
        raise ValueError("Unit dictionary must contain 'id' or 'ShortName' key.")

    unit_id = unit.id
    Update.update("Column", "UnitID", unit_id, column_id)

def get_column_method(project_id: bson.ObjectId, column_id_list: List[bson.ObjectId]) -> List[dict]:
    result = []

    columns = Column.objects(id__in=column_id_list, ProjectID=project_id)
    query = Q(id__in=columns.distinct("UnitID"), ProjectID=project_id) | Q(id__in=columns.distinct("UnitID"), Predefined=True)
    units = Unit.objects(query)
    unit_dict = {u.id: u.to_mongo() for u in units}

    for col in columns:
        col = col.to_mongo()
        if col["UnitID"] in unit_dict:
            col["unit"] = unit_dict[col["UnitID"]]
        else:
            col["unit"] = None
        result.append(col)

    return result

@bp.route("/<project_id>/column/<column_id>", methods=["GET"])
@bp.route("/<project_id>/columns/<column_id>", methods=["GET"])
@response_wrapper
def get_column(project_id: str, column_id: str):
    """
    Get column by ID
    ---
    """
    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    try:
        column_id = bson.ObjectId(column_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid column ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read columns in this project."
        )

    results = get_column_method(project_id, [column_id])
    result = results[0] if results else None
    if not result:
        raise ValueError("Column not found.")

    dumped_result = ColumnSchema().dump(result)
    return dumped_result

@bp.route('/<project_id>/column', methods=['GET'])
@bp.route('/<project_id>/columns', methods=['GET']) 
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_all(args, project_id: str):
    """
    Get all columns
    ---
    """
    
    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read columns in this project."
        )
    if args:
        id_list = get_id_list_from_request_and_check_permission("Column", args, "read", project_id=project_id, only_id_allowed=True)
        results = get_column_method(project_id, id_list)
        dumped = ColumnSchema().dump(results, many=True)

    else:
        raise ValueError("Request all columns not allowed.")

    return dumped

@bp.route("/<project_id>/column", methods=["POST"])
@bp.route("/<project_id>/columns", methods=["POST"])
@response_wrapper
def post(project_id: str):
    """
    Create a new data table
    ---
    """

    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="write")
    if not access:
        PermissionError(
            "You do not have permission to create or update a data table in this project."
        )
    data_list = get_json_from_request()
    data_list = ColumnPostSchema().load(data_list, many=True)
    return_id_list = []
    for data in data_list:
        column_id = update_or_create_column_method(data, project_id)
        return_id_list.append(column_id)
    return return_id_list


@bp.route("/<project_id>/column/<column_id>", methods=["DELETE"])
@bp.route("/<project_id>/columns/<column_id>", methods=["DELETE"])
@response_wrapper
def delete(project_id: str, column_id: str):
    """
    Delete a column by ID
    ---
    """
    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(
        project_id, flask.g.user, flag="delete"
    )
    if not access:
        PermissionError("You do not have permission to delete this column.")

    column_id = bson.ObjectId(column_id)
    column = Column.objects(id=column_id, ProjectID=project_id).first()
    if not column:
        raise ValueError("Column not found.")

    Delete.delete("Column", column_id)

    return column_id
