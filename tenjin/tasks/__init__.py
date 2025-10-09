import os

import redis
from redis import Redis
from flask import current_app
import flask
from rq import Worker as RQWorker
# from rq import SimpleWorker
from mongoengine import disconnect
from tenjin.cache import Cache

def create_redis_connection(app):
    redis_url = app.config["REDIS_URL"]
    redis_url = f"{redis_url}"
    conn = redis.from_url(redis_url, decode_responses=True)
    app.redis_connection = conn
    return conn


class Worker(RQWorker):
    def __init__(self, *args, **kwargs):
        # to avoid problems with the cache, the current app is passed to the worker and used for the app_context
        self.app = current_app
        super().__init__(*args, **kwargs)

    def execute_job(self, job, queue):
        super().execute_job(job, queue)
                
    def perform_job(self, job, queue):
        from tenjin.mongo_engine import Database
        # from tenjin.database.db import get_db
        # disconnect()
        with self.app.app_context():
            # db = get_db(force=True)
            # Cache.init_cache(self.app)
            Database.init_db(self.app)
            flask.g.user = job.kwargs["__user_id__"]
            if "__disable_access_check__" in job.kwargs:
                flask.g.no_access_check = job.kwargs.get("__disable_access_check__")
            try:
                job.kwargs.pop("__user_id__")
                job.kwargs.pop("__disable_access_check__")
                super().perform_job(job, queue)
            except Exception as e:
                raise e
            finally:
                flask.g.no_access_check = False





