import flask
from bson.objectid import ObjectId

# do not remove, used in eval.
from tenjin.logic.copy_template import copy
from tenjin.web.auth import login_required

bp = flask.Blueprint('copy-template', __name__)


@bp.route("/copy-template", methods=["POST"])
@login_required
def copy_template():
    data = flask.request.get_json()

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

    if collection.lower() == "experiments":
        collection = "Experiment"
    elif collection.lower() == "groups":
        collection = "Group"
    elif collection.lower() == "samples":
        collection = "Sample"
    else:
        collection = "ResearchItem"

    userID = flask.g.user
    templateID = ObjectId(templateID)
    projectID = ObjectId(projectID)
    try:
        groupID = ObjectId(groupid)
    except:
        groupID = None

    new_doc, mapping = copy(templateID, collection, projectID, userID, groupID,
                            include_fields, include_raw_data, include_files,
                            include_exp, include_sample, include_researchitem,
                            include_subgroup)
    return {
        'name': new_doc.Name,
        'id': str(new_doc.id),
    }
