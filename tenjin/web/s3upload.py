
import uuid

import flask
from flask_cors import CORS
from flask import request

from tenjin.execution.create import Create
from tenjin.database.db import get_db
from tenjin.file.s3 import check_s3, get_s3

from .auth import login_required

bp = flask.Blueprint('webs3upload', __name__)
# CORS(bp, origins="*", expose_headers=["X-API-KEY", "content-type"], allow_headers=["X-API-KEY", "content-type"],
#      methods=["GET", "POST", "OPTIONS"])
CORS(bp, origins="*")

@bp.route('/s3')
def s3_upload_enabled():
    return {'enabled': check_s3()}

# reference: https://github.com/transloadit/uppy/blob/main/packages/%40uppy/companion/src/server/controllers/s3.js

# bucket config https://uppy.io/docs/aws-s3-multipart/#S3-Bucket-Configuration


@bp.route('/s3/multipart', methods=['POST'])
@login_required
def s3_upload():
    data = request.get_json()
    userId = flask.g.user
    key = 's3multipart-'+str(uuid.uuid4())
    if data.get("createFileObject", True):
        fileId = Create.create("File", {
            "ChunkIDList": [],
            "Name": data['filename'],
            "S3Key": key
        }, get_db(), userId)
    s3data = get_s3().create_multipart_upload(
        Bucket=flask.current_app.config['S3_BUCKET'].lower(),
        Key=key,
        ACL='private',
        ContentType=data['type'],
        ContentDisposition="attachment; filename=\"" +
            data['filename']+"\"",
    )
    return {
        'key': s3data['Key'],
        'uploadId': s3data['UploadId'],
    }


@bp.route('/s3/multipart/<uploadId>', methods=['GET'])
@login_required
def get_uploaded_parts(uploadId):
    parts = get_s3().list_parts(
        Bucket=flask.current_app.config['S3_BUCKET'].lower(),
        Key=flask.request.args.get('key', ''),
        UploadId=uploadId,
        MaxParts=1000000,
    )
    return parts


@bp.route('/s3/multipart/<uploadId>/batch', methods=['GET'])
@login_required
def batch_sign_parts(uploadId):
    partNumbers = [int(i) for i in flask.request.args.get(
        'partNumbers', '').split(',')]
    presignedUrls = {pn: get_s3().generate_presigned_url(
        ClientMethod='upload_part',
        Params={
            'Bucket': flask.current_app.config['S3_BUCKET'].lower(),
            'Key': flask.request.args.get('key', ''),
            'UploadId': uploadId,
            'PartNumber': pn,
        },
        ExpiresIn=3600,
    ) for pn in partNumbers}
    return {'presignedUrls': presignedUrls}


@bp.route('/s3/multipart/<uploadId>/<partNumber>', methods=['GET'])
@login_required
def sign_part_upload(uploadId, partNumber):
    url = get_s3().generate_presigned_url(
        ClientMethod='upload_part',
        Params={
            'Bucket': flask.current_app.config['S3_BUCKET'].lower(),
            'Key': flask.request.args.get('key', ''),
            'UploadId': uploadId,
            'PartNumber': int(partNumber),
        },
        ExpiresIn=3600,
    )
    return {'url': url}


@bp.route('/s3/multipart/<uploadId>/complete', methods=['POST'])
@login_required
def complete_upload(uploadId):
    parts = flask.request.json['parts']
    new_parts = []
    for part in parts:
        p ={
            'ETag': part['ETag'],
            'PartNumber': part['PartNumber']
        }
        new_parts.append(p)
    data = get_s3().complete_multipart_upload(
        Bucket=flask.current_app.config['S3_BUCKET'].lower(),
        Key=flask.request.args.get('key', ''),
        UploadId=uploadId,
        MultipartUpload={
            'Parts': new_parts,
        },
    )
    return {'location': data['Location']}


@bp.route('/s3/multipart/<uploadId>', methods=['DELETE'])
@login_required
def abort_upload(uploadId):
    get_s3().abort_multipart_upload(
        Bucket=flask.current_app.config['S3_BUCKET'].lower(),
        Key=flask.request.args.get('key', ''),
        UploadId=uploadId,
    )
    return {}
