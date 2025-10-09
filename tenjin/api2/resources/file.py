import flask
import bson
from webargs.flaskparser import use_args

from tenjin.mongo_engine.File import File
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.ComboBoxEntry import ComboBoxEntry
from tenjin.mongo_engine.File import File

from tenjin.api2.schema.file_schema import FilePostSchema
from tenjin.api2.schema.inner_schema_collection import InnerSchemaWithoutShortID

from .helper_methods import (
    get_id_list_from_request_and_check_permission,
    response_wrapper,
    get_json_from_request,
)

from .fielddata import get_fielddata_method, update_or_create_fielddata_method
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete

from tenjin.file.file_storage import FileStorage
from tenjin.database.db import get_db


bp = flask.Blueprint("api2/comboboxentry", __name__)


@bp.route("/file/<file_id>", methods=["GET"])
@bp.route("/files/<file_id>", methods=["GET"])
@response_wrapper
def get_file_object(file_id: str):
    try:
        file_id = bson.ObjectId(file_id)
    except:
        raise ValueError("Invalid file ID.")
    
    file_object = File.objects(id=bson.ObjectId(file_id)).only("id", "Name" ).first()
    if not file_object:
        raise ValueError("File not found.")
    
    return_list, return_dict = File.check_permission([file_object.id], "read")
    if not return_list:
        raise PermissionError("You do not have permission to read this file.")

    file_object = file_object.to_mongo()
    dumped = InnerSchemaWithoutShortID().dump([file_object], many=True)

    return dumped

@bp.route("/file/<file_id>/content", methods=["GET"])
@bp.route("/files/<file_id>/content", methods=["GET"])
def get_file_content(file_id: str):

    try:
        file_id = bson.ObjectId(file_id)
    except:
        raise ValueError("Invalid file ID.")
    
    file_object = File.objects(id=bson.ObjectId(file_id)).only("id", "Name" ).first()
    if not file_object:
        raise ValueError("File not found.")
    
    return_list, return_dict = File.check_permission([file_object.id], "read")
    if not return_list:
        raise PermissionError("You do not have permission to read this file.")

    return FileStorage(get_db()).download(file_id)


@bp.route("/file", methods=["POST"])
@bp.route("/files", methods=["POST"])
@response_wrapper
def post_file():
    
    data_list = get_json_from_request()
    data_list = FilePostSchema().load(data_list, many=True)

    return_id_list = []
    for data in data_list:
        if "_id" not in data:
            # create new file
            if "Name" not in data:
                raise ValueError("Name is required to create a new file.")
            file_dict = {"Name": data["Name"]}
            file_id = Create.create("File", file_dict)
            data["_id"] = file_id
            data.pop("Name")
        if "_id" in data:
            try:
                file_id = bson.ObjectId(data["_id"])
            except:
                raise ValueError("Invalid file ID.")
            file_object = File.objects(id=bson.ObjectId(file_id)).only("id").first()
            if not file_object:
                raise ValueError("File not found.")
            return_list, return_dict = File.check_permission([file_object.id], "write")
            if not return_list:
                raise PermissionError("You do not have permission to update this file.")
            # update existing file
            direct_update_keys = ["Name", "S3Key"]
            for key in data:
                if key in direct_update_keys:
                    Update.update("File", key, data[key], file_id)

        return_id_list.append(file_id)
    
    return return_id_list
