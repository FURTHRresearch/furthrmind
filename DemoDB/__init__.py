import os
import time

import mimetypes
from threading import Thread
from queue import Queue
from tenjin import create_app


def restore_database(uri):
    file_path = os.path.abspath(__file__)
    file_path = file_path.replace("__init__.py", 'db')

    command_list = ["mongorestore", f"--uri='{uri}'", f"--dir='{file_path}'"]
    print(command_list)
    os.system(" ".join(command_list))
    restore_files()

def restore_files():
    from tenjin.mongo_engine.File import File
    from tenjin.mongo_engine.User import User
    path = os.path.abspath(__file__)
    path = path.replace("__init__.py", 'files')

    file_mapping = {}
    file_id_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_id = dirpath.replace(path, '')
            file_id = file_id.replace("/", '')
            file_id_list.append(file_id)
            file_mapping[file_id] = filename

    user = User.objects().first()

    queue = Queue()
    threadList = []
    for i in range(8):
        thread = Thread(target=upload_file, args=(queue,))
        threadList.append(thread)
        thread.start()

    files = File.objects(id__in=file_id_list)
    for file in files:
        if str(file.id) not in file_mapping:
            continue
        file_name = file_mapping[str(file.id)]
        file_path = f"{path}/{file.id}/{file_name}"
        job = {"file_path": file_path,
               "file_id": file.id,
               "file_name": file_name,
               "key": file.S3Key}
        queue.put(job)


    for thread in threadList:
        thread.join()

def upload_file(queue):
    from tenjin.file.s3 import get_s3

    started = False
    app = create_app(minimal=True)
    with app.app_context():
        while True:
            if queue.empty():
                if not started:
                    time.sleep(0.05)
                    continue
                break
            else:
                started = True
                job = queue.get()
                file_path = job.get("file_path")
                file_name = job.get("file_name")
                file_id = job.get("file_id")
                key = job.get("key")

                content_type = mimetypes.guess_type(file_name)[0]
                if not content_type:
                    content_type = "binary/octet-stream"
                with open(file_path, 'rb') as f:
                    get_s3().put_object(
                        Bucket=app.config['S3_BUCKET'].lower(),
                        Key=key,
                        Body=f.read(),
                        ContentDisposition="attachment; filename=\""+file_name+"\"",
                        ContentType=content_type,
                        ACL='private')
                print(f"restored file: {file_id}")
                queue.task_done()

if __name__ == '__main__':
    from tenjin.database.db import get_db
    from tenjin.MongoEngine import Database

    app = create_app(minimal=True)
    with app.app_context():
        Database.init_db(app)
        db = get_db()
        restore_files(db)