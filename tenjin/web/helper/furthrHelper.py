import flask
from tenjin.execution.append import Append
from tenjin.authentication import Authentication
import bson

from tenjin.database.db import get_db

def ensureAccess(collection, operation, targetId):
    userId = flask.g.user
    if not isinstance(targetId, bson.ObjectId):
        try:
            targetId = bson.ObjectId(targetId)
        except:
            flask.abort(403)
    if not Authentication.hasAccess(collection, operation, targetId, userId, get_db()):
        flask.abort(403)


def append(collection, field, targetId, value):
    userId = flask.g.user
    targetId = bson.ObjectId(targetId)
    ensureAccess(collection, "write", targetId)
    Append.append(collection, field, targetId, value, get_db(), userId)
