from redis import Redis
from rq import Queue
import flask.cli
import click
from flask import current_app

def makeTaskQueue(connection, db, emtpyQueue=False):
    queue = Queue(db, connection=Redis.from_url(connection))
    if emtpyQueue:
        queue.empty()
    return queue

@click.command('empty-queue')
@flask.cli.with_appcontext
def emptyTaskQueue():
    qs = current_app.config["REDIS_URL"]
    db = current_app.config["REDIS_DB"]

    queue = Queue(db, connection=Redis.from_url(qs))
    queue.empty()

def init_app(app):
    app.cli.add_command(emptyTaskQueue)


