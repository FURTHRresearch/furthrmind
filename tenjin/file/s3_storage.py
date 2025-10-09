import mimetypes
import pathlib
import uuid

import bson
import flask
from flask import current_app

from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.file.s3 import get_s3
import re
import os
from tenjin.mongo_engine.File import File

class S3Storage:

    def __init__(self, db):
        self.db = db
        mimetypes.add_type(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")

    def put(self, blob, fileID=None, fileName=None, userIDSet=True):
        if userIDSet:
            userID = flask.g.user
        else:
            userID = None
        if fileName is None:
            if fileID:
                file = File.objects(id=fileID).first()
                if file:
                    fileName = file.Name
            else:
                fileID = "pasted"

        fileName = re.sub('[^-a-zA-Z0-9_.() ]+', '', fileName)


        key = str(uuid.uuid4())
        get_s3().put_object(
            Bucket=flask.current_app.config['S3_BUCKET'].lower(),
            Key=key,
            Body=blob,
            ContentDisposition="attachment; filename=\"" + fileName + "\"",
            ContentType=mimetypes.guess_type(fileName)[0],
            ACL='private')

        if fileID is None:
            if fileName is None:
                fileName = "pasted"
            fileName = re.sub('[^-a-zA-Z0-9_.() ]+', '', fileName)
            fileID = Create.create("File", {
                "ChunkIDList": [],
                "Name": fileName,
                "S3Key": key
            }, self.db, userID)
        else:
            if type(fileID) is str:
                fileID = bson.objectid.ObjectId(fileID)

            Update.update("File", "S3Key",
                          key, fileID, self.db, userID)

        return fileID

    def putFromDisk(self, filepath, fileID=None, filename=''):
        userID = flask.g.user
        key = str(uuid.uuid4())

        if filename is None:
            filename = os.path.basename(filepath)
        filename = re.sub('[^-a-zA-Z0-9_.() ]+', '', filename)

        content_type = mimetypes.guess_type(filename)[0]
        if not content_type:
            content_type = "binary/octet-stream"
        with open(filepath, 'rb') as f:
            get_s3().put_object(
                Bucket=flask.current_app.config['S3_BUCKET'].lower(),
                Key=key,
                Body=f.read(),
                ContentDisposition="attachment; filename=\"" + filename + "\"",
                ContentType=content_type,
                ACL='private')

        if fileID is None:
            fileID = Create.create("File", {
                "ChunkIDList": [],
                "Name": filename,
                "S3Key": key
            }, self.db, userID)
        else:
            if type(fileID) is str:
                fileID = bson.objectid.ObjectId(fileID)
            Update.update("File", "S3Key",
                          key, fileID, self.db, userID)

        return fileID

    def download(self, id):
        file = self.db.db.File.find_one({'_id': bson.ObjectId(id)})
        key = file['S3Key'] if file['S3Key'] else id
        if pathlib.Path(file['Name']).suffix in ['.pdf', '.png', '.jpg', '.jpeg', '.mp4', '.txt']:
            obj = get_s3().get_object(
                Bucket=flask.current_app.config['S3_BUCKET'].lower(),
                Key=key)['Body'].read()
            resp = flask.current_app.response_class(
                obj, mimetype=mimetypes.guess_type(file['Name'])[0])
            if flask.request.args.get('view', False):
                resp.headers.set("Content-Disposition",
                                 "inline; filename=\""+file['Name']+"\"")
            else:
                resp.headers.set("Content-Disposition",
                                 "attachment; filename=\""+file['Name']+"\"")
            return resp
        return flask.redirect(
            get_s3().generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': flask.current_app.config['S3_BUCKET'].lower(), 'Key': key},
                ExpiresIn=300))

    def get_file(self, file_id):
        from tenjin.mongo_engine.File import File
        file = File.objects(id=file_id).first()
        key = file["S3Key"]
        try:
            s3_response_object = get_s3().get_object(
                Bucket=flask.current_app.config['S3_BUCKET'].lower(), Key=key)
            blob = s3_response_object['Body'].read()
        except:
            blob = None
        return blob

    def copy(self, file_id: bson.ObjectId):
        userID = flask.g.user
        file = self.db.db.File.find_one({'_id': file_id})
        key = file['S3Key'] if file['S3Key'] else str(file_id)
        bucket = current_app.config['S3_BUCKET'].lower()
        old_key = key
        new_key = str(uuid.uuid4())
        # copySource = {"Bucket": current_app.config['S3_BUCKET'].lower(),
        #               "Key": key}
        s3Instance = get_s3()

        try:
            s3Instance.copy_object(
                CopySource=f'/{bucket}/{old_key}',  # /Bucket-name/path/filename
                Bucket=bucket,  # Destination bucket
                Key=new_key  # Destination path/filename
            )
        except:
            pass

        fileDict = {
            "ChunkIDList": [],
            "Name": file["Name"],
            "S3Key": new_key}
        newFileID = Create.create("File", fileDict, self.db, userID)
        return newFileID

    def get_size(self, file_id: bson.ObjectId):
        from tenjin.mongo_engine.File import File
        file = File.objects(id=file_id).first()
        key = file["S3Key"]
        if not key:
            return
        try:
            s3_response_object = get_s3().head_object(
                Bucket=flask.current_app.config['S3_BUCKET'].lower(), Key=key)
            size = s3_response_object['ContentLength']
            return size
        except:
            pass
