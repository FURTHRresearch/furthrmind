# from gevent import monkey
# monkey.patch_all()


import os
import sys
from datetime import timedelta

import flask
import sentry_sdk
from flask import Flask
from flask_cors import CORS
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.serving import WSGIRequestHandler
import requests

from tenjin.tasks import rq_main
import tenjin.tasks
from tenjin.cache import Cache

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)


WSGIRequestHandler.protocol_version = "HTTP/1.1"

groups_per_page = 100


def create_app(minimal=False, app=None):
    if app is None:
        app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py', silent=True)
    if os.environ.get('TESTING'):
        if os.environ.get('TESTING').lower() == "true":
            app.config.from_pyfile('../tests/config.py', silent=True)


    app.redis_connection = None
    Cache.init_cache(app)

    @app.before_request
    def make_session_permanent():
        flask.session.permanent = True
        app.permanent_session_lifetime = timedelta(days=50)

    rq_enabled = app.config["REDIS_QUEUE_ENABLED"]
    if type(rq_enabled) is str:
        if rq_enabled.lower() == "true":
            rq_enabled = True
        else:
            rq_enabled = False
    if rq_enabled:
        qs = app.config["REDIS_URL"]
        db = app.config["REDIS_DB"]
        task_queue = rq_main.makeTaskQueue(qs, db, emtpyQueue=False)
        app.task_queue = task_queue
        tenjin.tasks.create_redis_connection(app)

    from .mongo_engine import Database
    Database.init_db(app)

    app.groups_per_page = groups_per_page

    if minimal:
        return app

    Database.run_ensure_indexes()

    send_bugs = app.config.get("SEND_BUG_REPORTS", False)
    if isinstance(send_bugs, str):
        if send_bugs.lower() == "true":
            send_bugs = True
        else:
            send_bugs = False
    if send_bugs:
        if app.config['GLITCHTIP_DSN']:
            sentry_sdk.init(
                dsn=app.config['GLITCHTIP_DSN'],
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0,
                profiles_sample_rate=0.1
            )

    if 'FLASK_ENV' not in os.environ or os.environ['FLASK_ENV'] != 'development':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True


    from tenjin.file import s3
    from tenjin.database import db
    db.init_app(app)
    s3.init_app(app)
    from .web import units
    units.init_app(app)

    from .web.helper import email_helper
    email_helper.init_app(app)

    from tenjin.database import database_version_update
    database_version_update.init_app(app)

    # from .mongo_engine import tests
    # tests.create_project()
    # with app.app_context():
    #     pass
    #     tests.check_request_list_with_lazy_ref()
        # tests.get_exp()
        # tests.create_combo()
        # tests.create_field_data()
        # tests.create_exp()
        # tests.create_user()
        # tests.in_operator_test()
        # tests.create_permission()
        # tests.create_supervisor()
        # tests.test_auth()
        # tests.create_research_item()
        #
        # tests.check_default()
        # return

    if rq_enabled:
        rq_main.init_app(app)


    # from . import app1
    # app.register_blueprint(app1.bp, url_prefix="/app1")

    # from . import api1
    # app.register_blueprint(api1.bp, url_prefix="/api1")

    from . import api2
    cors = CORS(app, resources={r"/api2/*": {"origins": "*"}})
    cors = CORS(app, resources={r"/web/files/*": {"origins": "*"}})
    cors = CORS(app, resources={r"/webdatacalc/*": {"origins": "*"}})
    # additonal cores in s3Upload

    # from tenjin import api2
    # app.register_blueprint(api2.bp, url_prefix="/api2")
    # from tenjin import web
    # app.register_blueprint(web.bp)

    # from tenjin.web import auth
    # app.register_blueprint(auth.bp)

    return app

