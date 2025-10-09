import json
from functools import wraps
import re
import requests

import bson
import flask
from flask import session
from tenjin.database.db import get_db

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.append import Append
from tenjin.execution.delete import Delete

bp = flask.Blueprint('webadmin', __name__)


def admin_only(f):
    @wraps(f)
    def decorated(*args, **kws):
        if not 'userID' in session or not session['userID']:
            flask.abort(403)
        flask.g.user = bson.ObjectId(flask.session['userID'])
        user = get_db().db.User.find_one(
            {'_id': flask.g.user})
        if not user or not user['Admin']:
            flask.abort(403)
        return f(*args, **kws)
    return decorated


@bp.route('/admin/users')
@admin_only
def get_all_users():
    return json.dumps([{
        'id': str(u['_id']),
        'firstName': u.get('FirstName', ''),
        'lastName': u.get('LastName', ''),
        'email': u.get('Email', ''),
        'admin': u.get('Admin', False),
        "avatar": '/files/' + str(u['ImageFileID']) if u.get('ImageFileID', False) else None,
    } for u in get_db().db.User.find().sort("Email", 1)])


@bp.route('/admin/users/<id>/supervisors')
@admin_only
def get_user_supervisors(id):
    return json.dumps([str(s['TopUserID']) for s in get_db().db.Supervisor.find({'SubUserID': bson.ObjectId(id)})])


@bp.route('/admin/users', methods=['POST'])
@admin_only
def create_user_route():
    data = flask.request.get_json()
    email = data['email']
    _id = create_user(email)
    return json.dumps({'id': str(_id)})

def create_user(email, user=None):
    _id = Create.create("User", {
        "Email": email}, get_db())
    if not isinstance(_id, bson.ObjectId):
        flask.abort(500, {"err": "Email address already exists."})

    """ add to mask project and to everybody group moved to user object in mongo_engine """
    # mask_project = get_db().db["Project"].find_one({"Name": "Maskentests_1"})
    # if mask_project:
    #     if mask_project["Info"] is not None:
    #         if mask_project["Info"].startswith("Discrepancy of particle"):
    #             permissionId = Create.create("Permission",
    #                                          {"ProjectID": bson.ObjectId(mask_project["_id"]),
    #                                           "Read": True,
    #                                           "Write": True,
    #                                           "Delete": True,
    #                                           "Invite": True})
    #             Append.append("User", "PermissionIDList", _id, permissionId, get_db(), flask.g.user)
    #
    # everybody_user_group = get_db().db["UserGroup"].find_one(
    #     {"Name": re.compile("everybody", re.IGNORECASE)})
    # if everybody_user_group:
    #     Append.append("UserGroup", "UserIDList", everybody_user_group["_id"], _id,
    #                   get_db(), everybody_user_group["OwnerID"])

    return str(_id)

@bp.route('/admin/users/<id>', methods=['DELETE'])
@admin_only
def delete_user(id):
    Delete.delete("User", bson.ObjectId(
        id), get_db(), flask.g.user)
    return 'done'


@bp.route('/admin/users/<id>', methods=['POST'])
@admin_only
def update_user(id):
    data = flask.request.get_json()
    Update.update("User", "FirstName", data['firstName'], bson.ObjectId(
        id), get_db(), flask.g.user)
    Update.update("User", "LastName", data['lastName'], bson.ObjectId(
        id), get_db(), flask.g.user)
    Update.update("User", "Admin", data['admin'], bson.ObjectId(
        id), get_db(), flask.g.user)
    Update.update("User", "Email", data['email'], bson.ObjectId(
        id), get_db(), flask.g.user)
    if data.get('password', False):
        # pwhash = bcrypt.hashpw(
        #     data['password'].encode(), bcrypt.gensalt()).decode()
        Update.update("User", "Password", data['password'], bson.ObjectId(
            id), get_db(), flask.g.user)

    newsupervisors = [bson.ObjectId(s) for s in data.get('supervisors', [])]
    oldSupervisors = [s['_id'] for s in get_db().db.Supervisor.find(
        {'SubUserID': bson.ObjectId(id)})]
    for os in oldSupervisors:
        if not os in newsupervisors:
            Delete.delete("Supervisor", os, get_db(),
                          flask.g.user)
    for ns in newsupervisors:
        if not ns in oldSupervisors:
            Create.create("Supervisor", {
                "TopUserID": ns,
                "SubUserID": bson.ObjectId(id)}, get_db(), flask.g.user)
    return 'done'


@bp.route('/admin/usergroups')
@admin_only
def get_usergroups():
    return json.dumps([{
        'id': str(u['_id']),
        'name': u.get('Name', ''),
        'users': [str(u) for u in u['UserIDList']],
    } for u in get_db().db.UserGroup.find().sort("Name", 1)])


@bp.route('/admin/usergroups/<id>', methods=['POST'])
@admin_only
def update_usergroup(id):
    data = flask.request.get_json()
    Update.update("UserGroup", "UserIDList", [bson.ObjectId(
        u) for u in data['users']], bson.ObjectId(id), get_db(), flask.g.user)
    return 'all good'


@bp.route('/admin/usergroups', methods=['POST'])
@admin_only
def add_usergroup():
    data = flask.request.get_json()
    id = Create.create("UserGroup", {
        "Name": data['name'],
    }, get_db(), flask.g.user)
    return {
        'id': str(id)
    }


@bp.route('/admin/usergroups/<id>', methods=['DELETE'])
@admin_only
def rm_usergroup(id):
    Delete.delete("UserGroup", bson.ObjectId(
        id), get_db(), flask.g.user)
    return 'done'
