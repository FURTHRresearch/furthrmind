import os

import bson
import bson.json_util
import flask


from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete
from tenjin.database.db import get_db
from .auth import login_required
from .helper.fieldsHelper import getFields
from .helper.furthrHelper import ensureAccess
from tenjin.web.helper.filterHelper import prepare_node

bp = flask.Blueprint('webgroups', __name__)


@bp.route('/groups/<id>', methods=['GET'])
@bp.route('/item/groups/<id>', methods=['GET'])
@login_required
def group_data(id):
    from tenjin.mongo_engine.Group import Group
    ensureAccess("Group", "read", id)
    db = get_db().db
    group = db.Group.find_one({"_id": bson.ObjectId(id)})
    fields = getFields(group['FieldDataIDList'])
    userId = flask.g.user
    return_dict = dict()
    return_dict["fields"] = fields
    return_dict["id"] = str(group['_id'])
    return_dict["name"] = group['Name']

    return_dict['writable'] = Group.check_permission_to_project(group["ProjectID"],
                                                                bson.ObjectId(userId),
                                                                "write")
    return_dict['admin'] = Group.check_permission_to_project(group["ProjectID"],
                                                             bson.ObjectId(userId),
                                                             "invite")
    return bson.json_util.dumps(return_dict)


@bp.route('/groups/<id>', methods=['DELETE'])
@login_required
def group_delete(id):
    ensureAccess("Group", "delete", id)
    Delete.delete("Group", bson.ObjectId(id), get_db(),
                  flask.g.user)
    return 'all done'


@bp.route('/groups/<id>', methods=['POST'])
@login_required
def update_group(id):
    ensureAccess("Group", "write", id)
    data = flask.request.get_json()
    userId = flask.g.user
    groupId = bson.ObjectId(id)
    if 'name' in data:
        Update.update("Group", "Name", data['name'], groupId, get_db(
        ), userId)  # do we need more validation?
    if 'fields' in data:
        Update.update("Group", "FieldDataIDList",
                      [bson.ObjectId(f) for f in data['fields']], groupId, get_db(), userId)
    return 'all done'


@bp.route('/groups/<id>/samples/name')
@login_required
def group_samples_name(id):
    # Access is given per group. All samples are accessible.
    ensureAccess("Group", "read", id)
    db = get_db().db
    samples = [{
        'id': str(s['_id']),
        'Name': s['Name']
    } for s in db.Sample
    .find({"GroupIDList": bson.ObjectId(id)})
    .sort('_id', -1)
    ]
    return bson.json_util.dumps(samples)


@bp.route('/groups/<id>/researchitems/name')
@login_required
def group_researchitems_name(id):
    # Access is given per group. All samples are accessible.
    ensureAccess("Group", "read", id)
    db = get_db().db
    researchitems = [{
        'id': str(s['_id']),
        'Name': s['Name']
    } for s in db.ResearchItem
    .find({"GroupIDList": bson.ObjectId(id)})
    .sort('_id', -1)
    ]
    return bson.json_util.dumps(researchitems)


@bp.route('/projects/<projid>/groups', methods=['POST'])
@login_required
def add_group(projid):
    # how to verify creates?
    userId = flask.g.user
    data = flask.request.get_json()
    name = data['name'] if 'name' in data else ''
    parent_group_id = data.get("groupid")

    parameter = {
        "Name": name,
        "ProjectID": bson.ObjectId(projid),
    }
    if parent_group_id and parent_group_id != "undefined":
        parent_group_id = bson.ObjectId(parent_group_id)
        parameter.update({"GroupID": parent_group_id})

    if not parent_group_id:
        parent_group_id = 0
    else:
        parent_group_id = str(parent_group_id)
    group = Create.create("Group", parameter, get_db(), userId, return_document=True)
    
    group_node = prepare_node(item_id=group.id, 
                              item_name=group.Name, 
                              item_short_id=group.ShortID,
                              group_id=group.id,
                              parent_id=parent_group_id,
                              category="Groups",
                              droppable=True,
                              expandable=True)

    return group_node


@bp.route('/groups/<id>/experiments', methods=['POST'])
@login_required
def group_create_exp(id):
    ensureAccess("Group", "write", id)
    userId = flask.g.user
    data = flask.request.get_json()
    name = data['name'] if data.get(
        'name', False) else 'New Experiment ' + str(os.urandom(6).hex())
    exp = Create.create("Experiment", {
        "GroupIDList": [bson.ObjectId(id)],
        "Name": name
    }, get_db(), userId, return_document=True)
    category = "Experiments"
    node_id = f"{id}/sep/{category}"
    exp_node = prepare_node(item_id=exp.id,
                            item_name=name,
                            item_short_id=exp.ShortID,
                            group_id=id,
                            parent_id=node_id,
                            category=category,
                            droppable=False,
                            expandable=False)
    cat_node = prepare_node(item_id=node_id,
                            item_name=category,
                            item_short_id="",
                            group_id=id,
                            parent_id=id,
                            category=category,
                            droppable=False,
                            expandable=True)
    return {"node": exp_node, "cat_node": cat_node}



@bp.route('/groups/<id>/samples', methods=['POST'])
@login_required
def group_create_sample(id):
    ensureAccess("Group", "write", id)
    userId = flask.g.user
    data = flask.request.get_json()
    name = data['name'] if data.get(
        'name', False) else 'New Sample ' + str(os.urandom(6).hex())
    sample = Create.create("Sample", {
        "GroupIDList": [bson.ObjectId(id)],
        "Name": name
    }, get_db(), userId, return_document=True)
    
    category = "Samples"
    node_id = f"{id}/sep/{category}"
    
    sample_node = prepare_node(item_id=sample.id,
                            item_name=name,
                            item_short_id=sample.ShortID,
                            group_id=id,
                            parent_id=node_id,
                            category=category,
                            droppable=False,
                            expandable=False)
    cat_node = prepare_node(item_id=node_id,
                            item_name=category,
                            item_short_id="",
                            group_id=id,
                            parent_id=id,
                            category=category,
                            droppable=False,
                            expandable=True)
    return {"node": sample_node, "cat_node": cat_node}


@bp.route('/groups/<id>/researchitems', methods=['POST'])
@login_required
def group_create_researchitem(id):
    ensureAccess("Group", "write", id)
    userId = flask.g.user
    data = flask.request.get_json()
    name = data['name'] if data.get(
        'name', False) else 'New Research item ' + str(os.urandom(6).hex())
    research_category_id = bson.ObjectId(data["research_category_id"])
    research_category = get_db().db.ResearchCategory.find_one({"_id": research_category_id})
    researchitem = Create.create("ResearchItem", {
        "GroupIDList": [bson.ObjectId(id)],
        "Name": name,
        "ResearchCategoryID": research_category_id
    }, get_db(), userId, return_document=True)
    
    category = research_category["Name"]
    node_id = f"{id}/sep/{category}"
    ri_node = prepare_node(item_id=researchitem.id,
                            item_name=name,
                            item_short_id=researchitem.ShortID,
                            group_id=id,
                            parent_id=node_id,
                            category=category,
                            droppable=False,
                            expandable=False)
    cat_node = prepare_node(item_id=node_id,
                            item_name=category,
                            item_short_id="",
                            group_id=id,
                            parent_id=id,
                            category=category,
                            droppable=False,
                            expandable=True)
    return {"node": ri_node, "cat_node": cat_node}

