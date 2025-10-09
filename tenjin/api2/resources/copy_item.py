import flask
from bson import ObjectId

from tenjin.api2.schema.copy_item_schema import CopyItemPostSchema
from tenjin.api2.schema.inner_schema_collection import InnerSchemaWithoutShortID

from .helper_methods import (
    get_json_from_request,
    response_wrapper
)
from tenjin.logic.copy_template import copy
from tenjin.mongo_engine import Database
from tenjin.mongo_engine.Project import Project
from tenjin.mongo_engine.Group import Group


bp = flask.Blueprint("api2/copyitem", __name__)


@bp.route("/copy-item", methods=["POST"])
@response_wrapper
def copy_item():
    
    data_list = get_json_from_request()
    data_list = CopyItemPostSchema().load(data_list, many=True)
    
    # only one item at a time
    data = data_list[0]
    
    collection = data.get('collection', '')
    templateID = data.get('sourceId', '')
    projectID = data.get('targetProject', '')
    groupid = data.get('targetGroup', '')
    include_exp = data.get('includeExps', False)
    include_sample = data.get('includeSamples', False)
    include_researchitem = data.get('includeResearchItems', False)
    include_subgroup = data.get('includeSubgroups', False)
    include_raw_data = data.get('includeRawData', False)
    include_files = data.get('includeFiles', False)
    include_fields = data.get('includeFields', False)
    
    
    if collection.lower().startswith("experiment"):
        collection = "Experiment"
    elif collection.lower().startswith("group"):
        collection = "Group"
    elif collection.lower().startswith("sample"):
        collection = "Sample"
    else:
        collection = "ResearchItem"
        
    userID = flask.g.user
    templateID = ObjectId(templateID)
    projectID = ObjectId(projectID)
    
    cls = Database.get_collection_class(collection)
    result_list, result_dict = cls.check_permission([templateID], "read")
    if not result_list:
        raise PermissionError(
            "You do not have permission to read this template."
        )
    access = Project.check_permission_to_project(projectID, flask.g.user, flag="write")
    if not access:
        raise PermissionError(
            "You do not have permission to write to this project."
        )
    
    Project
    
    try:
        groupID = ObjectId(groupid)
        result_list, result_dict = Group.check_permission([groupID], "write")
        if not result_list:
            raise PermissionError(
                "You do not have permission to write to this group."
            )
    except:
        groupID = None

    new_doc, mapping = copy(templateID, collection, projectID, userID, groupID,
                            include_fields, include_raw_data, include_files,
                            include_exp, include_sample, include_researchitem,
                            include_subgroup)
    result =  {
        'Name': new_doc.Name,
        '_id': str(new_doc.id),
    }

    dumped = InnerSchemaWithoutShortID().dump(result)
    return dumped