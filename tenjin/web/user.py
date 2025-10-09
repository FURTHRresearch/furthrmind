import io
import json
import os

import bcrypt
import bson
import flask
from flask import request, render_template
import requests

import re
from PIL import Image

from tenjin.web.auth import createNewApiKey
from tenjin.database.db import get_db
from tenjin.file.file_storage import FileStorage

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.append import Append
from tenjin.web.helper.email_helper import send_email
from .auth import login_required
from tenjin.tasks.rq_task import create_task

bp = flask.Blueprint('webuser', __name__)


@bp.route('/user')
@login_required
def get_user_infos():
    db = get_db().db
    user = db.User.find_one({'_id': flask.g.user})
    try:
        date = user['Date'].isoformat()
    except:
        date = None

    return {
        "id": str(user['_id']),
        "email": user['Email'],
        "firstName": user['FirstName'],
        "lastName": user['LastName'],
        "avatar": '/files/' + str(user['ImageFileID']) if user['ImageFileID'] else None,
        "memberSince": date,
        "admin": user['Admin']
    }


@bp.route('/user', methods=['POST'])
@login_required
def update_user():
    db = get_db().db
    data = flask.request.get_json()
    if "firstName" in data:
        Update.update("User", "FirstName", data["firstName"], flask.g.user)
    if "lastName" in data:
        Update.update("User", "LastName", data["lastName"], flask.g.user)

    if "password" in data:
        user = db.User.find_one({'_id': flask.g.user})
        if not bcrypt.checkpw(data['password'].encode(), user['Password'].encode()):
            flask.abort(403)
        if "newPassword" in data:
            # password = bcrypt.hashpw(data['newPassword'].encode(), bcrypt.gensalt()).decode()
            Update.update("User", "Password", data["newPassword"], flask.g.user)

        if "email" in data:
            token = str(os.urandom(16).hex())
            db.EmailUpdateRequest.insert_one(
                {'user': flask.g.user, 'email': data['email'], 'token': token})
            link = flask.current_app.config['ROOT_URL'] + \
                '/confirm-new-email?token=' + token

            body = render_template('emails/new_email.html', link=link)
            create_task(send_email, data['email'], 'FURTHRmind account', body)


    return 'all good'


@bp.route('/confirm-new-email', methods=['GET'])
def confirm_new_email():
    from tenjin.mongo_engine import Database
    db = get_db().db
    token = flask.request.args.get('token')
    updateRequest = db.EmailUpdateRequest.find_one({'token': token})
    if not updateRequest:
        return 'invalid token'
    try:
        Database.set_no_access_check(True)
        Update.update("User", "Email", updateRequest['email'], updateRequest["user"])
    except Exception as e:
        raise e
    finally:
        Database.set_no_access_check(False)

    # db.User.update_one({'_id': updateRequest['user']}, {
    #                    '$set': {'Email': updateRequest['email']}})
    db.EmailUpdateRequest.delete_one({'token': token})
    return "Email updated. <a href='/'>Back to FURTHRmind</a>"


@bp.route('/user/avatar', methods=['POST'])
@login_required
def update_avatar():
    file = flask.request.files['file']
    fs = FileStorage(get_db())
    im = Image.open(file)
    im.thumbnail((200, 200))
    imexp = io.BytesIO()
    im.save(imexp, format='PNG')
    userId = flask.g.user
    fileId = fs.put(imexp.getbuffer(
            ).tobytes(), fileName=f"{userId}_avatar.png")
    Update.update("User", "ImageFileID", fileId,
                  userId, get_db(), userId)
    return {
        "fileId": str(fileId)
    }


@bp.route('/signup', methods=['POST'])
def signup():
    data = flask.request.get_json()
    if not 'email' in data:
        flask.abort(400, 'email is missing')

    # pwhash = bcrypt.hashpw(os.urandom(16).hex().encode(),
    #                        bcrypt.gensalt()).decode()

    if flask.current_app.config['ALLOWED_SIGNUP_DOMAIN'] == "":
        email = data['email']
    else:

        if f"@{flask.current_app.config['ALLOWED_SIGNUP_DOMAIN']}" in data['email']:
            email = data['email']
        else:
            email = data['email'] + '@' + flask.current_app.config['ALLOWED_SIGNUP_DOMAIN']

    doc = {
        "Email": email,
        "Admin": False,
        "Password": os.urandom(16).hex(),
        "FirstName": data['firstName'] if 'firstName' in data else '',
        "LastName": data['lastName'] if 'lastName' in data else '',
    }

    userId = Create.create("User", doc, get_db(), None)
    if not isinstance(userId, bson.ObjectId):
        flask.abort(500, {"err": "Email address already in use"})


    """ add to mask project and to everybody group moved to user object in mongo_engine """
    # mask_project = get_db().db["Project"].find_one({"Name": "Maskentests_1"})
    # if mask_project:
    #     if mask_project["Info"] is not None:
    #         if mask_project["Info"].startswith("Discrepancy of particle"):
    #             flask.g.user = mask_project["OwnerID"]
    #             permissionId = Create.create("Permission",
    #                                          {"ProjectID": bson.ObjectId(mask_project["_id"]),
    #                                           "Read": True,
    #                                           "Write": True,
    #                                           "Delete": True,
    #                                           "Invite": True},
    #                                          get_db(), mask_project["OwnerID"])
    #             Append.append("User", "PermissionIDList", userId, permissionId, get_db(), mask_project["OwnerID"])
    #
    # everybody_user_group = get_db().db["UserGroup"].find_one(
    #     {"Name": re.compile("everybody", re.IGNORECASE)})
    # if everybody_user_group:
    #     flask.g.user = everybody_user_group["OwnerID"]
    #     Append.append("UserGroup", "UserIDList", everybody_user_group["_id"], userId,
    #                   get_db(), everybody_user_group["OwnerID"])

    """ Email send from User Object (mongo_engine)"""
    # token = str(os.urandom(16).hex())
    # get_db().db.PasswordReset.insert_one(
    #     {'email': email, 'token': token})
    #
    # link = flask.current_app.config['ROOT_URL'] + \
    #     '/set-password?token=' + token
    #
    # body = render_template('emails/new_account.html', email=email, link=link)
    # send_email(email, 'FURTHRmind account', body)

    return 'all good'

@bp.route('/signup', methods=['GET'])
def signup_get():
    return flask.send_from_directory('tenjin/web/static', 'react/index.html')


@bp.route('/users', methods=['GET'])
@login_required
def check_user_by_email():
    db = get_db().db
    email = flask.request.args.get('email')
    user = db.User.find_one({'Email': email})
    if not user:
        flask.abort(404)
    return {
        "id": str(user['_id']),
        "name": user['FirstName'] + ' ' + user['LastName'],
        "avatar": '/files/' + str(user['ImageFileID']) if user.get('ImageFileID', False) else None
    }


@bp.route('/userlist')
@login_required
def get_userlist():
    users = get_db().db.User.find().sort("Email",1)
    user_list = []
    for u in users:
        if u.get("Email") is None:
            continue
        user_list.append(
            {
                'id': str(u['_id']),
                'firstName': u.get('FirstName', ''),
                'lastName': u.get('LastName', ''),
                'email': u.get('Email', ''),
                "avatar": '/files/' + str(u['ImageFileID']) if u.get('ImageFileID', False) else None,
            }
        )
    return json.dumps(user_list)


@bp.route('/usergroups')
@login_required
def get_usergroups():
    return json.dumps([{
        'id': str(g['_id']),
        'name': g.get('Name', ''),
    } for g in get_db().db.UserGroup.find().sort("Name", 1)])


@bp.route('/apikeys', methods=['GET'])
@login_required
def get_apikeys():
    return json.dumps([{
        'id': str(k['_id']),
        'name': k.get('Name', 'unnamed'),
        'creationTime': k.get('Date').isoformat() if k.get('Date') else '',
    } for k in get_db().db.ApiKey.find({'UserID': flask.g.user, "Name": {"$ne": "WebDataCalcKey"}}).sort('Date', -1)])


@bp.route('/apikeys', methods=['POST'])
@login_required
def create_apikey():
    name = flask.request.get_json().get('name', '')
    key = createNewApiKey(flask.g.user, 24*365*100, name, get_db().db)
    apikey = get_db().db.ApiKey.find_one({'KeyString': key})
    return {
        'key': key,
        'id': str(apikey['_id']),
        'name': name,
        'creationTime': str(apikey.get('Date')),
    }


@bp.route('/apikeys/<id>', methods=['DELETE'])
@login_required
def delete_apikey(id):
    get_db().db.ApiKey.delete_one({'_id': bson.ObjectId(
        id), 'UserID': flask.g.user})
    return 'ok'
