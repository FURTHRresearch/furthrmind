from .s3_storage import S3Storage

import bson


class FileStorage:
    chunkSize = 8196000

    def __init__(self, db):
        self.db = db

    def put(self, blob, file_id=None, fileName=None, userIDSet=True):
        fs = S3Storage(self.db)
        return fs.put(blob, file_id, fileName, userIDSet)

    def putFromDisk(self, file, file_id = None, filename=''):
        fs = S3Storage(self.db)
        return fs.putFromDisk(file, file_id, filename)

    def download(self, file_id):
        return S3Storage(self.db).download(file_id)

    def get_file(self, file_id):
        fs = S3Storage(self.db)
        return fs.get_file(file_id)

    def copy(self, _id: bson.objectid.ObjectId):
        fs = S3Storage(self.db)
        newFileID = fs.copy(_id)
        return newFileID

    def get_size(self, file_id: bson.ObjectId):
        fs = S3Storage(self.db)
        size = fs.get_size(file_id)
        return size
