from functools import wraps

import flask

from tenjin.authentication import Authentication

bp = flask.Blueprint('api1auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kws):
        if not Authentication.authenticate_user():
            flask.abort(403)
        return f(*args, **kws)
    return decorated
