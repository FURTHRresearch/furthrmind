import flask
from .auth import login_required
from flask import request
from tenjin.database.db import get_db
import uuid
import tempfile
import re
import base64

from tenjin.file.file_storage import FileStorage

bp = flask.Blueprint('webupload', __name__)


@bp.route('/tus-upload', methods=['POST', 'OPTIONS'])
@login_required
def tus_upload():
    res = flask.make_response("", 200)
    if request.method == 'OPTIONS' and request.headers.get('Access-Control-Request-Method', None) is not None:
        return res  # CORS
    res.headers['Tus-Resumable'] = '1.0.0'
    res.headers['Tus-Version'] = '1.0.0'
    if request.method == 'OPTIONS':
        res.headers['Tus-Extension'] = 'creation'
        res.headers['Tus-Max-Size'] = 4294967296
        res.status_code = 204
        return res

    file_size = int(request.headers.get("Upload-Length", "0"))
    resource_id = str(uuid.uuid4())

    f = tempfile.NamedTemporaryFile(delete=False)
    f.seek(file_size - 1)
    f.write(b"\0")
    f.close()

    filename = base64.b64decode(re.search(
        'filename (.*?)($|,)', request.headers.get("Upload-Metadata", "")).group(1)).decode('ascii')

    get_db().db.TUSUpload.insert_one({
        'uuid': resource_id,
        'size': file_size,
        'offset': 0,
        'tempfile': f.name,
        'filename': filename
    })

    res.status_code = 201
    res.headers['Location'] = '/tus-upload/' + resource_id
    res.headers['Tus-Temp-Filename'] = resource_id
    res.autocorrect_location_header = False

    return res


@bp.route('/tus-upload/<resource_id>', methods=['HEAD', 'PATCH', 'DELETE'])
@login_required
def tus_upload_chunk(resource_id):
    res = flask.make_response("", 204)
    res.headers['Tus-Resumable'] = '1.0.0'
    res.headers['Tus-Version'] = '1.0.0'
    db = get_db().db

    tusdata = db.TUSUpload.find_one({'uuid': resource_id})
    if not tusdata or not 'offset' in tusdata:
        flask.abort(404)

    if request.method == 'HEAD':
        res.status_code = 200
        res.headers['Upload-Offset'] = tusdata['offset']
        res.headers['Upload-Length'] = tusdata['size']
        res.headers['Cache-Control'] = 'no-store'
        return res

    file_offset = int(request.headers.get("Upload-Offset", 0))
    chunk_size = int(request.headers.get("Content-Length", 0))
    file_size = tusdata['size']

    f = open(tusdata['tempfile'], "r+b")
    f.seek(file_offset)
    f.write(request.data)
    f.close()
    db.TUSUpload.update_one({'uuid': resource_id}, {
                            '$set': {'offset': file_offset + chunk_size}})

    res.headers['Upload-Offset'] = file_offset + chunk_size

    if file_size == file_offset + chunk_size:
        fs = FileStorage(get_db())
        fileId = fs.putFromDisk(tusdata['tempfile'], file_id=None, filename=tusdata['filename'])
        get_db().db.File.update_one(
            {'_id': fileId}, {'$set': {'uuid': resource_id}})
        db.TUSUpload.delete_one({'uuid': resource_id})
    return res
