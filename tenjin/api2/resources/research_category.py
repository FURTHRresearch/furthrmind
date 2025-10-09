import bson
import flask
from webargs.flaskparser import use_args


from tenjin.api2.schema.research_category_schema import (
    ResearchCategorySchema,
    ResearchCategoryPostSchema,
)

from tenjin.api2.resources.datatable import update_or_create_datatable_method

from tenjin.execution.update import Update
from tenjin.execution.create import Create
from tenjin.execution.delete import Delete

from .helper_methods import (
    get_id_list_from_request_and_check_permission,
    response_wrapper,
    get_json_from_request,
)

from tenjin.api2.schema.query_input_schema import QueryInputSchema
from tenjin.api2.schema.get_all_standard_schema import GetAllStandardSchema

from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.ResearchCategory import ResearchCategory

bp = flask.Blueprint("api2/reseach_category", __name__)


@bp.route("/<project_id>/category/<item_id>", methods=["GET"])
@bp.route("/<project_id>/categories/<item_id>", methods=["GET"])
@bp.route("/<project_id>/researchcategory/<item_id>", methods=["GET"])
@bp.route("/<project_id>/researchcategories/<item_id>", methods=["GET"])
@response_wrapper
def get(project_id: str, item_id: str):
    """
    Get a research category by id.
    """
    project_id = bson.ObjectId(project_id)
    item_id = bson.ObjectId(item_id)

    try:
        project_id = bson.ObjectId(project_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid project ID format.")
    try:
        item_id = bson.ObjectId(item_id)
    except bson.errors.InvalidId:
        raise ValueError("Invalid category data ID format.")
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read category data in this project."
        )

    item = ResearchCategory.objects(
        id=item_id,
        ProjectID=project_id,
    ).first()
    if item is None:
        raise ValueError("Research category not found.")
    dumped = ResearchCategorySchema().dump([item], many=True)
    return dumped


@bp.route("/<project_id>/category", methods=["GET"])
@bp.route("/<project_id>/categories", methods=["GET"])
@bp.route("/<project_id>/researchcategory", methods=["GET"])
@bp.route("/<project_id>/researchcategories", methods=["GET"])
@use_args(QueryInputSchema(), location="query")
@response_wrapper
def get_many(args, project_id: str):
    """
    Get many research categories.
    """
    project_id = bson.ObjectId(project_id)

    access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
    if not access:
        raise PermissionError(
            "You do not have permission to read category data in this project."
        )

    if args:
        id_list = get_id_list_from_request_and_check_permission(
            "ResearchCategory", args, "read", project_id=project_id
        )
        categories = ResearchCategory.objects(id__in=id_list, ProjectID=project_id)
        dumped = ResearchCategorySchema().dump(list(categories), many=True)
    else:
        access = Project.check_permission_to_project(project_id, flask.g.user, flag="read")
        if not access:
            raise PermissionError(
                "You do not have permission to read columns in this project."
            )
        categories = ResearchCategory.objects(ProjectID=project_id)
        dumped = GetAllStandardSchema().dump(list(categories), many=True)

    return dumped


@bp.route("/<project_id>/category", methods=["POST"])
@bp.route("/<project_id>/categories", methods=["POST"])
@bp.route("/<project_id>/researchcategory", methods=["POST"])
@bp.route("/<project_id>/researchcategories", methods=["POST"])
@response_wrapper
def post(project_id: str):
    data_list = get_json_from_request()
    data_list = ResearchCategoryPostSchema().load(data_list, many=True)

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(project_id, flask.g.user, flag="write")
    if not access:
        PermissionError(
            "You do not have permission to create or update a group in this project."
        )
    cat_ids = []
    for data in data_list:
        if "_id" not in data:
            # create new
            if "Name" not in data:
                raise ValueError("Name is required to create a research category.")
            param = {
                "ProjectID": project_id,
                "Name": data["Name"],
            }

            cat_id = Create.create("ResearchCategory", param)
            data["_id"] = str(cat_id)
            data.pop("Name")
            
        
        if "_id" in data:
            
            # update existing
            try:
                cat_id = bson.ObjectId(data.pop("_id"))
            except bson.errors.InvalidId:
                raise ValueError("Invalid category ID format.")
            existing = ResearchCategory.objects(
                id=cat_id,
                ProjectID=project_id,
            ).first()
            if existing is None:
                raise ValueError("Research category not found.")
            cat_ids.append(str(cat_id))
            direct_update_keys = ["Name", "Description"]
            for key in data:
                if key in direct_update_keys:
                    Update.update("ResearchCategory", key, data[key], cat_id)
            
    return cat_ids


@bp.route("/<project_id>/category/<cat_id>", methods=["DELETE"])
@bp.route("/<project_id>/categories/<cat_id>", methods=["DELETE"])
@bp.route("/<project_id>/researchcategory/<cat_id>", methods=["DELETE"])
@bp.route("/<project_id>/researchcategories/<cat_id>", methods=["DELETE"])
@response_wrapper
def delete(project_id: str, cat_id: str):
    """
    Delete a category by ID
    ---
    """

    project_id = bson.ObjectId(project_id)
    access = Project.check_permission_to_project(
        project_id, flask.g.user, flag="delete"
    )
    if not access:
        PermissionError("You do not have permission to delete this field.")

    cat_id = bson.ObjectId(cat_id)
    category = ResearchCategory.objects(id=cat_id, ProjectID=project_id).first()
    if not category:
        raise ValueError("Category not found.")

    Delete.delete("ResearchCategory", cat_id)

    return cat_id