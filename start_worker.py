import sys
import time
import os

from rq import Queue
from rq.worker_pool import WorkerPool
from redis import Redis

# Preload libraries
from tenjin import create_app
from tenjin.tasks import Worker


app = create_app(minimal=True)
# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with app.app_context():
    from tenjin.web.helper.email_helper import send_email
    from tenjin.logic.copy_template import copy_one_data_table
    from tenjin.logic.copy_template import copy_files
    from tenjin.mongo_engine.ImportCollections import *
    print(sys.path)
    import tenjin
    # while True:
    qs = app.config["REDIS_URL"]
    db = app.config["REDIS_DB"]
    queue = Queue(db, connection=Redis.from_url(qs))
    # count = SimpleWorker.count(queue=queue)
    # print("Before cleaning", count)
    # worker_registration.clean_worker_registry(queue)
    # count = SimpleWorker.count(queue=queue)
    # print("After clening", count)
    # if count > 0:
    #     time.sleep(5)
    #     continue
    num_worker = app.config["NUM_WORKER"]
    worker_pool = WorkerPool(queues=[db], connection=Redis.from_url(qs), num_workers=num_worker, worker_class=Worker)
    worker_pool.start()


            # w = Worker(db, Redis.from_url(qs))
            # w.work()

