import bson
import flask
from typing import List
from webargs.flaskparser import use_args

from tenjin.api2.schema.datatable_schema import DataTableSchema, DataTablePostSchema
from tenjin.api2.schema.get_all_standard_schema import GetAllStandardSchema
from tenjin.api2.schema.query_input_schema import QueryInputSchema

from tenjin.api2.resources.helper_methods import response_wrapper, get_json_from_request
from tenjin.api2.resources.helper_methods import get_id_list_from_request_and_check_permission

from tenjin.api2.schema.group_schema import GroupSchema
from tenjin.execution.update import Update
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete


from tenjin.mongo_engine.Project import Project

from tenjin.mongo_engine.RawData import RawData
from tenjin.mongo_engine.Column import Column
from tenjin.mongo_engine.Experiment import Experiment
from tenjin.mongo_engine.Sample import Sample
from tenjin.mongo_engine.ResearchItem import ResearchItem
from mongo_engine.Project import Project


bp = flask.Blueprint("api2/datatable", __name__)

def update_or_create_datatable_method(
    args: dict, project_id: bson.ObjectId
) -> bson.ObjectId:
    """
    Process field data from any other collection.
    """
    if "_id" not in args:
        if "Name" not in args:
            raise ValueError("Name is required to create a new datatable.")
        datatable_id = create_datatable(args["Name"], project_id)

        args["_id"] = datatable_id

    if "_id" in args:
        datatable_id = bson.ObjectId(args["_id"])
        if "columns" in args:
            column_id_list = [c["_id"] for c in args["columns"]]
            columns = Column.objects(id__in=column_id_list).only("id")
            existing_column_id_list = [col.id for col in columns]
            column_id_list = [col_id for col_id in column_id_list if col_id in existing_column_id_list]
            Update.update("RawData", "ColumnIDList", column_id_list, datatable_id)
        if "exp" in args:
            exp_id = bson.ObjectId(args["exp"]["_id"])
            exp = Experiment.objects(id=exp_id, ProjectID=project_id).only("id").first()
            if exp is not None:
                Update.update("RawData", "ExpID", exp_id, datatable_id)
        if "sample" in args:
            sample_id = bson.ObjectId(args["sample"]["_id"])
            sample = Sample.objects(id=sample_id, ProjectID=project_id).only("id").first()
            if sample is not None:
                Update.update("RawData", "SampleID", sample_id, datatable_id)
        if "researchitem" in args:
            research_item_id = bson.ObjectId(args["researchitem"]["_id"])
            research_item = ResearchItem.objects(id=research_item_id, ProjectID=project_id).only("id").first()
            if research_item is not None:
                Update.update("RawData", "ResearchItemID", research_item_id, datatable_id)

    return datatable_id


def create_datatable(name, project_id):

    parameter = {
        "Name": name,
        "ProjectID": project_id
    }
    
    datatable_id = Create.create("RawData", parameter)
    return datatable_id


def get_datatable_method(project_id: bson.ObjectId, datatable_id_list: List[bson.ObjectId]) -> List[dict]:
    result = []

    rawdata = RawData.objects(id__in=datatable_id_list, ProjectID=project_id)
    columns = Column.objects(id__in=rawdata.distinct("ColumnIDList"), ProjectID=project_id).only("id", "Name")
    column_dict = {col.id: col.to_mongo() for col in columns}


    result = []
    for rd in rawdata:
        rd = rd.to_mongo()
        rd["columns"] = [column_dict.get(c_id) for c_id in rd["ColumnIDList"] if c_id in column_dict]
        result.append(rd)

    return result


@bp.route("/<project_id>/datatable/<datatable_id>", methods=["GET"])
@bp.route("/<project_id>/datatables/<datatable_id>", methods=["GET"])
@bp.route("/<project_id>/rawdata/<datatable_id>", methods=["GET"])
@response_wrapper
def get_datatable(project_id: str, datatable_id: str):
    """
    Get data table by ID
    ---
    """
    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    try:
        datatable_id = bson.ObjectId(datatable_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid data table ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read data tables in this project."
        )

    results = get_datatable_method(project_id, [datatable_id])
    result = results[0] if results else None
    if not result:
        raise ValueError("Field data not found.")
    
    dumped_result = DataTableSchema().dump(result)
    return dumped_result

@bp.route('/<project_id>/datatable', methods=['GET'])
@bp.route('/<project_id>/datatables', methods=['GET']) 
@bp.route('/<project_id>/rawdata', methods=['GET']) 
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_all(args, project_id: str):
    """
    Get all data tables
    ---
    """
    
    project_id = bson.ObjectId(project_id)

    if args:
        id_list = get_id_list_from_request_and_check_permission("RawData", args, "read", project_id=project_id, only_id_allowed=True)
        results = get_datatable_method(project_id, id_list)
        dumped = DataTableSchema().dump(results, many=True)

    else:
        access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
        if not access:
            raise PermissionError(
                "You do not have permission to read columns in this project."
            )
        datatables = RawData.objects(ProjectID=project_id).only("id", "Name")
        dumped = GetAllStandardSchema().dump(list(datatables), many=True)
    
    return dumped


@bp.route("/<project_id>/datatable", methods=["POST"])
@bp.route("/<project_id>/datatables", methods=["POST"])
@bp.route("/<project_id>/rawdata", methods=["POST"])
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
    data_list = DataTablePostSchema().load(data_list, many=True)
    return_id_list = []
    for data in data_list:
        datatable_id = update_or_create_datatable_method(data, project_id)
        return_id_list.append(datatable_id)
    return return_id_list


@bp.route("/<project_id>/datatable/<datatable_id>", methods=["DELETE"])
@bp.route("/<project_id>/datatables/<datatable_id>", methods=["DELETE"])
@bp.route("/<project_id>/rawdata/<datatable_id>", methods=["DELETE"])
@response_wrapper
def delete(project_id: str, datatable_id: str):
    """
    Delete a data table by ID
    ---
    """
    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(
        project_id, flask.g.user, flag="delete"
    )
    if not access:
        PermissionError("You do not have permission to delete this data table.")

    datatable_id = bson.ObjectId(datatable_id)
    datatable = RawData.objects(id=datatable_id, ProjectID=project_id).first()
    if not datatable:
        raise ValueError("Data table not found.")

    Delete.delete("RawData", datatable_id)

    return datatable_id
