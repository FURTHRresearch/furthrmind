import mimetypes
import tempfile
import uuid
from queue import Queue
from threading import Thread

import boto3
import click
import flask
from flask import current_app, g

from tenjin.database.db import get_db


class S3Instance:
    s3 = None


def get_s3() -> boto3.Session.client:
    if S3Instance.s3 is None:
        session = boto3.session.Session()
        S3Instance.s3 = session.client('s3',
                                       region_name=current_app.config['S3_REGION'],
                                       endpoint_url=current_app.config['S3_ENDPOINT'],
                                       aws_access_key_id=current_app.config['S3_KEY'],
                                       aws_secret_access_key=current_app.config['S3_SECRET'])
    return S3Instance.s3


def check_s3():
    return current_app.config['S3_ENDPOINT'] != ''


def close_s3(e=None):
    g.pop('s3', None)


@click.command('s3-cors')
@flask.cli.with_appcontext
def update_cors():
    execute_cors_method()

def execute_cors_method():
    if not check_s3():
        return
    response = get_s3().list_buckets()
    if response.get("Buckets"):
        buckets = [bucket["Name"] for bucket in response.get("Buckets")]

        if current_app.config["S3_BUCKET"].lower() not in buckets:
            bucket = get_s3().create_bucket(Bucket=current_app.config["S3_BUCKET"].lower())
            print("bucket created")
    response = get_s3().list_buckets()
    if response.get("Buckets"):
        buckets = [bucket["Name"] for bucket in response.get("Buckets")]
        print("Buckets: ", buckets)

    cors = {
        'CORSRules': [{
            'AllowedMethods': ['GET', 'PUT'],
            'AllowedOrigins': ['*'],
            "AllowedHeaders": [
                "Authorization",
                "x-amz-date",
                "x-amz-content-sha256",
                "content-type"
            ],
            "ExposeHeaders": ["ETag", "x-amz-meta-custom-header"],
            'MaxAgeSeconds': 3000
        }]
    }
    try:
        get_s3().put_bucket_cors(
            Bucket=current_app.config["S3_BUCKET"], CORSConfiguration=cors)
    except:
        pass

@click.command('migrate-files')
@flask.cli.with_appcontext
def migrate_files():
    db = get_db().db
    files = list(db.File.find({'ChunkIDList': {'$not': {'$size': 0}}}))
    print('Migrating files...')
    print('Found {} files with chunks'.format(len(files)))

    bucket = current_app.config['S3_BUCKET'].lower()
    queue = Queue()
    s3 = get_s3()

    for file in files:
        queue.put(dict(file))

    def inner(queue: Queue):
        while True:
            if queue.empty():
                break
            else:
                file = queue.get()
                print('Migrating file {}'.format(file['_id']))
                with tempfile.NamedTemporaryFile() as t:
                    for chunkId in file['ChunkIDList']:
                        chunk = db.Chunk.find_one({'_id': chunkId})
                        t.write(chunk['Data'])
                    t.seek(0)

                    key = '_migrated/' + str(uuid.uuid4())
                    mimetype = mimetypes.guess_type(file['Name'])[0]
                    s3.upload_fileobj(
                        t, bucket, key, ExtraArgs={
                            'ContentType': mimetype if mimetype else 'binary/octet-stream',
                            'ContentDisposition': "inline; filename=\""+file['Name']+"\"",
                        })
                    db.File.update_one({'_id': file['_id']},
                                       {'$set': {'ChunkIDList': [], 'S3Key': key}})

    threadList = []
    for i in range(8):
        thread = Thread(target=inner, args=(queue,))
        threadList.append(thread)
        thread.start()

    for thread in threadList:
        thread.join()

    print('Done')

@click.command('migrate-files-from-other-s3')
@click.option('--endpoint')
@click.option('--bucket')
@click.option('--region')
@click.option('--key')
@click.option('--secret')
@flask.cli.with_appcontext
def migrate_from_other_s3(endpoint, bucket, region, key, secret):
    print(endpoint, bucket)
    queue = Queue()
    db = get_db().db
    original_s3 = get_s3()
    original_bucket = flask.current_app.config['S3_BUCKET'].lower()
    session = boto3.session.Session()
    other_s3 = session.client('s3',
                              region_name=region,
                              endpoint_url=endpoint,
                              aws_access_key_id=key,
                              aws_secret_access_key=secret)
    files = db.File.find({})
    for file in files:
        queue.put(dict(file))

    def inner(queue: Queue):
        while True:
            if queue.empty():
                break
            else:
                file = queue.get()
                if file["S3Key"]:
                    exception = False
                    try:
                        s3_response_object = other_s3.get_object(
                            Bucket=bucket.lower(), Key=file["S3Key"])
                        blob = s3_response_object["Body"].read()
                        print("File downloaded")
                    except Exception as e:
                        print(e)
                        exception = True
                        print(file["_id"], file["S3Key"], "not successful")
                    if not exception:
                        try:
                            content_type = mimetypes.guess_type(file["Name"])[0]
                            if content_type is None:
                                content_type = "text/plain"
                            original_s3.put_object(
                                Bucket=original_bucket,
                                Key=file["S3Key"],
                                Body=blob,
                                ContentDisposition="attachment; filename=\"" + file["Name"] + "\"",
                                ContentType=content_type,
                                ACL='private')
                            print("File copied")
                        except Exception as e:
                            print(e)
                            print("File not copied")
                queue.task_done()

    threadList = []
    for i in range(8):
        thread = Thread(target=inner, args=(queue,))
        threadList.append(thread)
        thread.start()

    for thread in threadList:
        thread.join()

    print('Done')

@click.command('delete-not-used-s3-keys')
@flask.cli.with_appcontext
def delete_not_used_s3_keys():
    session = boto3.session.Session()
    s3 = session.resource('s3',
                                   region_name=current_app.config['S3_REGION'],
                                   endpoint_url=current_app.config['S3_ENDPOINT'],
                                   aws_access_key_id=current_app.config['S3_KEY'],
                                   aws_secret_access_key=current_app.config['S3_SECRET'])

    objects = s3.Bucket(current_app.config['S3_BUCKET']).objects.all()
    from tenjin.mongo_engine.File import File

    deleted_keys = []
    for obj in objects:
        key = obj.key
        file = File.objects(S3Key=key).first()
        if not file:
            obj.delete()
            deleted_keys.append(key)
    print('Deleted keys:', len(deleted_keys))


def init_app(app):
    app.teardown_appcontext(close_s3)
    app.cli.add_command(update_cors)
    app.cli.add_command(migrate_files)
    app.cli.add_command(migrate_from_other_s3)
    app.cli.add_command(delete_not_used_s3_keys)

