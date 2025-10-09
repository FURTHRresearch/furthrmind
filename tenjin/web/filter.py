import bson

from .auth import login_required
import flask
from tenjin.mongo_engine.Filter import Filter
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete

bp = flask.Blueprint('filter', __name__)


@bp.route('/project/<project_id>/filter', methods=['GET'])
@login_required
def get_filter(project_id):
    filter_objects = Filter.objects(ProjectID=bson.ObjectId(project_id))
    result = []
    for f in filter_objects:
        result.append({
            'id': str(f['id']),
            'name': f['Name'],
            "project_id": str(project_id),
            "displayed_columns": f['DisplayedColumns'],
            "filter_list": f['FilterList'],
            "name_filter": f['NameFilter'],
            "include_linked": f["IncludeLinked"],
            "displayed_categories": f["DisplayedCategories"]
        })
    return result

@bp.route('/project/<project_id>/filter', methods=['POST'])
@login_required
def create_filter(project_id):
    data = flask.request.get_json()
    param = {
        "Name": data['name'],
        "ProjectID": bson.ObjectId(project_id),
        "DisplayedColumns": data['displayed_columns'],
        "FilterList": data['filter_list'],
        "NameFilter": data['name_filter'],
        "IncludeLinked": data['include_linked'],
        "DisplayedCategories": data['displayed_categories'],
    }
    filter_id = Create.create("Filter", param)
    result = {
        'id': str(filter_id),
        'name': param['Name'],
        "project_id": str(project_id),
        "displayed_columns": param['DisplayedColumns'],
        "filter_list": param['FilterList'],
        "name_filter": param['NameFilter'],
        "include_linked": param["IncludeLinked"],
        "displayed_categories": param["DisplayedCategories"]
    }
    return result

@bp.route('/filter/<filter_id>', methods=['POST'])
@login_required
def update_filter(filter_id):
    filter_id = bson.ObjectId(filter_id)

    data = flask.request.get_json()

    if "name" in data:
        Update.update("Filter", "Name", data["name"], filter_id)
    if "displayed_columns" in data:
        Update.update("Filter", "DisplayedColumns", data["displayed_columns"], filter_id)
    if "filter_list" in data:
        Update.update("Filter", "FilterList", data["filter_list"], filter_id)
    if "name_filter" in data:
        Update.update("Filter", "NameFilter", data["name_filter"], filter_id)
    if "include_linked" in data:
        Update.update("Filter", "IncludeLinked", str(data["include_linked"]), filter_id)
    if "displayed_categories" in data:
        Update.update("Filter", "DisplayedCategories", data["displayed_categories"], filter_id)

    return "Done"

@bp.route('/project/<project_id>/filter/check', methods=['POST'])
@login_required
def check_filter_name(project_id):
    data = flask.request.get_json()
    param = {
        "ProjectID": bson.ObjectId(project_id),
        "Name": data["name"],
    }

    doc = Filter(**param)
    try:
        doc.validate(clean=True)
        return str(True)
    except:
        return str(False)


@bp.route('filter/<filter_id>/check', methods=['POST'])
@login_required
def check_filter_name_update(filter_id):
    data = flask.request.get_json()
    doc = Filter.objects(id=bson.ObjectId(filter_id)).first()
    doc.Name = data["name"]
    try:
        doc.validate(clean=True)
        return str(True)
    except:
        return str(False)

@bp.route('/filter/<filter_id>', methods=['DELETE'])
@login_required
def delete_filter(filter_id):
    filter_id = bson.ObjectId(filter_id)
    Delete.delete("Filter", filter_id)

    return "Done"
