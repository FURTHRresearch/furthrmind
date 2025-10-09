import json

import bson
import flask
from tenjin.file.file_storage import FileStorage
from tenjin.database.db import get_db

from tenjin.authentication import Authentication

from .auth import login_required


bp = flask.Blueprint('webfiles', __name__)


@bp.route('/files/<fileid>')
@bp.route('/nbfiles/<fileid>')
@login_required
def file(fileid):
    # return ""
    if not Authentication.hasAccess("File", "read", bson.ObjectId(fileid), flask.g.user, get_db()):
        flask.abort(403)
    ffs = FileStorage(get_db())
    return ffs.download(fileid)


@bp.route('/files/<id>/data', methods=['GET'])
@login_required
def get_file_name(id):
    if not Authentication.hasAccess("File", "read", bson.ObjectId(id), flask.g.user, get_db()):
        flask.abort(403)
    file = get_db().db.File.find_one({'_id': bson.ObjectId(id)})
    return {
        'name': file['Name'],
        'id': id
    }


@bp.route("/files/uuid/<uuids>")
@login_required
def get_file_from_uuid(uuids):
    uuid_list = uuids.split(",")
    if not uuid_list:
        return {}
    if "s3multipart-" in uuid_list[0]:
        key = "S3Key"
    else:
        key = "uuid"
    files = get_db().db.File.find({key: {"$in": uuid_list}})
    file_list = []
    for f in files:
        file_list.append({
            'name': f['Name'],
            'id': str(f["_id"])
        })
    return json.dumps(file_list)


@bp.route('/files', methods=['POST'])
@login_required
def create_file():
    uuid = flask.request.json.get('uuid')
    if "s3multipart-" in uuid:
        file = get_db().db.File.find_one({'S3Key': uuid})
    else:
        file = get_db().db.File.find_one({"uuid": uuid})
    return {'id': str(file['_id'])}
